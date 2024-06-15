#include <exception>
#include <iostream>
#include <cstdlib>
#include <filesystem>
#include <sstream>
#include <sys/stat.h>
#include <sys/types.h>
#include <map>
#include <vector>
#include <string>

#include <canlib.h>
#include <kvmlib.h>
#include <kvlclib.h>
#include <kvaDbLib.h>

#include <indicators/progress_bar.hpp>
#include <indicators/cursor_control.hpp>

#include <yaml-cpp/yaml.h>

class CanBaseException : public std::exception {
public:
    const char* what() const noexcept override { return err_txt; }
protected:
    char err_txt[256] = { 0 };
};

class KvmException : public CanBaseException {
public:
    kvmStatus status;
    KvmException(kvmStatus s) : status(s) {
        kvmGetErrorText(status, err_txt, sizeof(err_txt));
        snprintf(err_txt + strlen(err_txt), sizeof(err_txt) - strlen(err_txt),
            "(%d) :", status);
    }
    static kvmStatus throw_on_error(kvmStatus s) {
        if (s != kvmOK) {
            if (s == kvmERR_FILE_ERROR) {
                std::cerr << "SD Card not found!" << std::endl;
                std::exit(1); // Exit the program with code 1
            }
            throw KvmException(s);
        }
        return s;
    };
};


class KvlcException : public CanBaseException {
public:
    KvlcStatus status;
    KvlcException(KvlcStatus s) : status(s) {
        kvlcGetErrorText(status, err_txt, sizeof(err_txt));
        snprintf(err_txt + strlen(err_txt), sizeof(err_txt) - strlen(err_txt),
            "(%d) :", status);
    }
    static KvlcStatus throw_on_error(KvlcStatus s) {
        if (s != kvlcOK)
            throw KvlcException(s);
        return s;
    };
};

struct DbcConfig {
    std::string relativePath;
    std::string channelMask;
};

class MDF4Converter {
private:
    KvlcHandle h;
public:
    MDF4Converter(const std::string& outpath) {
        uint32_t yes = 1;
        KvlcException::throw_on_error(kvlcCreateConverter(&h, outpath.c_str(),KVLC_FILE_FORMAT_MDF_4X_SIGNAL));
        KvlcException::throw_on_error(kvlcFeedSelectFormat(h, KVLC_FILE_FORMAT_MEMO_LOG));
        KvlcException::throw_on_error(kvlcSetProperty(h, KVLC_PROPERTY_OVERWRITE, &yes, sizeof(yes)));
    }
    ~MDF4Converter() {
        KvlcException::throw_on_error(kvlcDeleteConverter(h));
    }

    void convert_event(kvmLogEventEx& e) {
        KvlcException::throw_on_error(kvlcFeedLogEvent(h, &e));
        KvlcException::throw_on_error(kvlcConvertEvent(h));
    }


    void addDatabaseFile(const std::string& path, unsigned int channelMask) {
        KvlcException::throw_on_error(kvlcAddDatabaseFile(h, path.c_str(), channelMask));
        //std::cout << "Adding DBC file: " << path << " with channel mask: " << channelMask << std::endl;
    }
};

std::vector<DbcConfig> loadConfig(const std::string& filename) {
    YAML::Node config = YAML::LoadFile(filename);
    std::vector<DbcConfig> dbcFiles;

    for (const auto& node : config["dbc_files"]) {
        DbcConfig dbcConfig;
        dbcConfig.relativePath = node["relativepath"].as<std::string>();
        dbcConfig.channelMask = node["channel_mask"].as<std::string>();
        dbcFiles.push_back(dbcConfig);
    }

    return dbcFiles;
}

void add_dbc_files_from_config(MDF4Converter& kc, const std::string& basePath, std::string configFilePath) {
    std::vector<DbcConfig> dbcFiles = loadConfig(configFilePath);

    // Mapping from string to ChannelMask Bitmask
    std::map<std::string, unsigned int> channelMaskMapping = {
        {"ONE", 1},
        {"TWO", 2},
        {"THREE", 4},
        {"FOUR", 8},
        {"FIVE", 16}
    };

    // Iterate through each DBC file configuration and add them.
    for (const auto& dbcConfig : dbcFiles) {
        std::string fullPath = (std::filesystem::path(basePath) / dbcConfig.relativePath).string();
        auto it = channelMaskMapping.find(dbcConfig.channelMask);

        if (it == channelMaskMapping.end()) {
            throw std::invalid_argument("Invalid channel mask: " + dbcConfig.channelMask);
        }

        unsigned int channelMask = it->second;
        kc.addDatabaseFile(fullPath, channelMask);
    }
}

std::vector<int> parseNumbers(const std::string& input) {
    std::vector<int> logstoexport;
    std::istringstream ss(input);
    std::string token;
    while (std::getline(ss, token, ',')) {
        try {
            int num = std::stoi(token);
            logstoexport.push_back(num);
        } catch (const std::invalid_argument& e) {
            std::cerr << "Invalid number: " << token << std::endl;
        } catch (const std::out_of_range& e) {
            std::cerr << "Number out of range: " << token << std::endl;
        }
    }
    return logstoexport;
}

std::string unix_to_iso_with_underscores(time_t unixTimestamp) {
    struct tm timeInfo;
    if (localtime_s(&timeInfo, &unixTimestamp) != 0) {
        return "Invalid timestamp";
    }

    char isoTimestamp[20];
    strftime(isoTimestamp, sizeof(isoTimestamp), "%Y%m%d_%H%M%S", &timeInfo);
    return isoTimestamp;
}

int main(int argc, char* argv[]) {
    // Check if the correct number of arguments are provided
    if (argc < 4) {
        std::cerr << "Usage: " << argv[0] << " config.yml Location 1,2,4,16,37" << std::endl;
        return 1;
    }

    // Read arguments
    std::string configFile = argv[1];
    std::string location = argv[2];
    std::string numbersArg = argv[3];
    
    // Parse numbers
    std::vector<int> logstoexport = parseNumbers(numbersArg);

    // Print parsed values for verification
    std::cout << "Config File: " << configFile << std::endl;
    std::cout << "Location: " << location << std::endl;
    std::cout << "Numbers: ";
    for (int num : logstoexport) {
        std::cout << num << " ";
    }
    std::cout << std::endl;


    kvmStatus status;
    kvmInitialize();

    int32_t ldfMajor = 0;
    int32_t ldfMinor = 0;
    int32_t kvmDEVICE = 1;

    uint32_t nr_logfiles;
    int16_t converted_count = 0;

    const char* inputfilename = "E:/LOG00000.KMF";

    kvmHandle kvm_handle = kvmKmfOpenEx(inputfilename, &status, kvmDEVICE, &ldfMajor, &ldfMinor);

    KvmException::throw_on_error(status);

    KvmException::throw_on_error(kvmDeviceMountKmfEx(kvm_handle, &ldfMajor, &ldfMinor));

    KvmException::throw_on_error(kvmLogFileGetCount(kvm_handle, &nr_logfiles));

    // Hide cursor
    indicators::show_console_cursor(false);
    //for (size_t log_nr = 4; log_nr < nr_logfiles; log_nr++) {

    for (uint16_t log_nr = 1; log_nr < nr_logfiles; log_nr++) {
        // Check if log_nr is in log_numbers_to_run
        if (std::find(logstoexport.begin(), logstoexport.end(), log_nr) != logstoexport.end()) {
        
            int64_t event_count;
            kvmLogEventEx e;
            KvmException::throw_on_error(kvmLogFileMountEx(kvm_handle, log_nr, &event_count));

            // Create output file path, C++14 needed for std::filesystem.
            std::filesystem::path outpath = "export";

            uint32_t start_time;
            uint32_t end_time;
            kvmLogFileGetStartTime(kvm_handle, &start_time);
            kvmLogFileGetEndTime(kvm_handle, &end_time);

            uint32_t duration = end_time - start_time;

            outpath /= unix_to_iso_with_underscores(start_time).substr(0, 8) + "_" + location;
            outpath /= unix_to_iso_with_underscores(start_time) + "_" + location + "_" + std::to_string(duration) + "s" ".mf4";

            std::filesystem::create_directories(outpath.parent_path());

            std::cout << "Exporting log to: " << std::filesystem::absolute(outpath) << std::endl;
            MDF4Converter conv(outpath.string());

            // Add DBC files to the converter.
            //std::string basePath = "C:/Users/Zbook15uG5/Documents/GitHub/DataProcessing/"; // Change this to your base path
            std::string basePath = std::filesystem::path(argv[0]).parent_path().string();
            add_dbc_files_from_config(conv, basePath, configFile);

            std::cout << "Rough Event Estimate: " << event_count << std::endl;


            int64_t counter = 0;
            int64_t update_frequency = 100000;
            int64_t total_bar = event_count / update_frequency;

            using namespace indicators;
            ProgressBar bar{
              option::BarWidth{50},
              option::ForegroundColor{Color::white},
              option::FontStyles{
                    std::vector<FontStyle>{FontStyle::bold}},
              option::MaxProgress{total_bar},
            };

            while ((status = kvmLogFileReadEvent(kvm_handle, &e)) != kvmERR_NOLOGMSG) {

                KvmException::throw_on_error(status);
                conv.convert_event(e);

                ++counter;
                if (counter == update_frequency) {
                    bar.tick();
                    counter = 0;
                }           
            }
            bar.set_progress(100);
            indicators::show_console_cursor(true);


            converted_count++;
            // Print status message
            std::cout << "Status: Log " << converted_count << " of " << logstoexport.size() << " converted." << std::endl;

            //std::cout << "Conversion finished"<< std::endl;
    }   
    }

    exit(0);
}