from canlib import kvlclib
import yaml
from alive_progress import alive_bar
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

        
def try_set_propery(converter, property, value=None):
    # Check if the format supports the given property
    if converter.format.isPropertySupported(property):
        # If a value is specified, set the property to this value
        if value is not None:
            converter.setProperty(property, value)

        # Get the property's default value
        default = converter.format.getPropertyDefault(property)
        print(f'  {property} is supported (Default: {default})')

        # Get the property's current value
        value = converter.getProperty(property)
        print(f'    Current value: {value}')
    else:
        print(f'  {property} is not supported')

def add_dbc_files_from_config(config, kc):
    # Load the YAML configuration file
    #with open(config_path, 'r') as file:
    #    config = yaml.safe_load(file)

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
                    #print("About %d events left to convert..." % kc.eventCount())

            except kvlclib.KvlcEndOfFile:
                
                bar(1)

                if kc.isOverrunActive():
                    print("NOTE! The extracted data contained overrun.")
                    kc.resetOverrunActive()
                if kc.isDataTruncated():
                    print("NOTE! The extracted data was truncated.")
                    kc.resetStatusTruncated()
                break
        bar(total - bar.current)
    print("%s done" % kc.getOutputFilename())

def convert_single_file(file, folder_path, config):


    inputfile = os.path.join(folder_path, file)
    print("Input filename is '%s'" % inputfile)
    # Set output format
    fmt = kvlclib.WriterFormat(kvlclib.FILE_FORMAT_MDF_4X_SIGNAL)

    print("Output format is '%s'" % fmt.name)
    
    # Set resulting output filename
    outfile = os.path.join(folder_path, os.path.splitext(file)[0] + "." + fmt.extension)
    print("Output filename is '%s'" % outfile)

    # Create converter
    kc = kvlclib.Converter(outfile, fmt)


    # Add DBC files from config file
    add_dbc_files_from_config(config, kc)

    # Set input filename and format
    
    kc.setInputFile(inputfile, file_format=kvlclib.FILE_FORMAT_KME50)

    try_set_propery(kc, kvlclib.PROPERTY_OVERWRITE, 1)

    try_set_propery(kc, kvlclib.Property.COMPRESSION_LEVEL, 1)

    #try_set_propery(kc, kvlclib.Property.CROP_PRETRIGGER)

    #try_set_propery(kc, kvlclib.Property.SIGNAL_BASED)

    #trySetProperty(kc, kvlclib.Property.COMPRESSION_LEVEL, 0)

    print("break")

    # Convert all events
    convertEvents(kc)

    
    

def multiprocessing_convert_files_in_folder(folder_path, config):
    # Get list of all files in the specified folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = [executor.submit(convert_single_file, file, folder_path, config) for file in files]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error occurred: {e}")

def convert_files_in_folder(folder_path, config_path):
    # Get list of all files in the specified folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    # Process each file sequentially
    for file in files:
        try:
            convert_single_file(file, folder_path, config_path)
            os.remove(os.path.join(folder_path, file))

        except Exception as e:
            print(f"Error occurred while processing {file}: {e}") 

                  
def directmf4(file, folder_path, config):

    fmt = kvlclib.WriterFormat(kvlclib.FILE_FORMAT_MDF_4X_SIGNAL)
    print("Output format is '%s'" % fmt.name)
    
    # Set resulting output filename
    outfile = os.path.join(folder_path, os.path.splitext(file)[0] + "." + fmt.extension)
    print("Output filename is '%s'" % outfile)

    # Create converter
    kc = kvlclib.Converter(outfile, fmt)


    # Add DBC files from config file
    add_dbc_files_from_config(config, kc)











# Set the folder path and config file path
#folder_path = './result'
#config_file_path = 'config.yml'

# Convert all files in the specified folder
#convert_files_in_folder(folder_path, config_file_path)