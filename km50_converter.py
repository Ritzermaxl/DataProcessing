from canlib import kvlclib
import yaml
from alive_progress import alive_bar

def trySetProperty(converter, property, value=None):
    # Check if the format supports the given property
    if converter.format.isPropertySupported(property):

        # If a value was specified, set the property to this value
        if value is not None:
            converter.setProperty(property, value)

        # get the property's default value
        default = converter.format.getPropertyDefault(property)
        print(" PROPERTY_%s is supported (Default: %s)" %
              (property['name'], default))

        # get the property's current value
        value = converter.getProperty(property)
        print("	Current value: %s" % value)
    else:
        print(" PROPERTY %s is not supported" %
              (property['name']))

def add_dbc_files_from_config(config_file):
    # Load the YAML configuration file
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    # Mapping from string to kvlclib.ChannelMask enum
    channel_mask_mapping = {
        'ONE': kvlclib.ChannelMask.ONE,
        'TWO': kvlclib.ChannelMask.TWO,
        'THREE': kvlclib.ChannelMask.THREE,
        'FOUR': kvlclib.ChannelMask.FOUR,
        'FIVE': kvlclib.ChannelMask.FIVE,
        # Add more mappings as needed
    }
    
    # Iterate through each DBC file configuration and add them
    for dbc_config in config['dbc_files']:
        path = dbc_config['path']
        channel_mask_str = dbc_config['channel_mask']
        
        if channel_mask_str not in channel_mask_mapping:
            raise ValueError(f"Invalid channel mask: {channel_mask_str}")
        
        channel_mask = channel_mask_mapping[channel_mask_str]
        kc.addDatabaseFile(path, channel_mask)


def convertEvents(kc):
    # Get estimated number of remaining events in the input file. This can be
    # useful for displaying progress during conversion.
    total = kc.eventCount()
    print("Converting about %d events..." % total)
    with alive_bar(total) as bar:
        while True:
            try:
                # Convert events from input file one by one until EOF is reached
                kc.convertEvent()
                bar()
                if kc.isOutputFilenameNew():
                    print("New output filename: %s" % kc.getOutputFilename())
                    print("About %d events left to convert..." % kc.eventCount())
                    
            except kvlclib.KvlcEndOfFile:
                if kc.isOverrunActive():
                    print("NOTE! The extracted data contained overrun.")
                    kc.resetOverrunActive()
                if kc.isDataTruncated():
                    print("NOTE! The extracted data was truncated.")
                    kc.resetStatusTruncated()
                break

# set output format
fmt = kvlclib.WriterFormat(kvlclib.FILE_FORMAT_MDF_4X_SIGNAL)
# the name of the formatter is fetched using kvlcGetWriterName() internally
print("Output format is '%s'" % fmt.name)

# set resulting output filename taking advantage of the extension defined
# in the format. (Uses kvlcGetWriterExtension() under the hood.)
outfile = "myresult." + fmt.extension
print("Output filename is '%s'" % outfile)

# create converter
kc = kvlclib.Converter(outfile, fmt)


config_file_path = 'config.yml'
add_dbc_files_from_config(config_file_path)

# add database file
#channel_mask = kvlclib.ChannelMask.ONE #| kvlclib.ChannelMask.TWO
#kc.addDatabaseFile("./CanNetworks2024/system_can.dbc", channel_mask)

# Set input filename and format
inputfile = "log_73-30130-00832-8_10097_006.kme50"
print("Input filename is '%s'" % inputfile)
kc.setInputFile(inputfile, file_format=kvlclib.FILE_FORMAT_KME50)

# allow output file to overwrite existing files
trySetProperty(kc, kvlclib.PROPERTY_OVERWRITE, 1)

# add nice header to the output file
#trySetProperty(kc, kvlclib.PROPERTY_WRITE_HEADER, 1)

# we are converting CAN traffic with max 8 bytes, so we can minimize the
# width of the data output to 8 bytes
#trySetProperty(kc, kvlclib.PROPERTY_LIMIT_DATA_BYTES, 8)

# convert all events
convertEvents(kc)