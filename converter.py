from canlib import kvlclib, EAN, VersionNumber, kvmlib
import yaml
from alive_progress import alive_bar
import os
from InquirerPy.base.control import Choice


def listfiles(config):
    filename = config['inputfilename']
    with kvmlib.openKmf(filename) as kmf:
        ldf_version = kmf.log.ldf_version
        #print(ldf_version)
        if ldf_version != VersionNumber(major=5, minor=0):
            if ldf_version == VersionNumber(major=3, minor=0):
                raise ValueError('This log file can be read if you reopen the'
                                ' device as kvmDEVICE_MHYDRA.')
            raise ValueError('Unexpected Lio Data Format: ' + str(ldf_version))
        
        num_log_files = len(kmf.log)
        filelist = []
        for i, log_file in enumerate(kmf.log):
            name = "File {index}: {start}-{duration}s, approx {num} events.".format(
                index=i,
                start=log_file.start_time,
                num=log_file.event_count_estimation(),
                duration=int((log_file.start_time - log_file.end_time).total_seconds()),
            )
            filelist.append(Choice(i, name))

    return filelist

def add_dbc_files_from_config(config, kc):
    #   Load all the DBC files specified in the configuration file into the converter
    gitpath = config['gitpath']
    # Mapping from string to kvlclib.ChannelMask enum
    channel_mask_mapping = {
        'ONE': kvlclib.ChannelMask.ONE,
        'TWO': kvlclib.ChannelMask.TWO,
        'THREE': kvlclib.ChannelMask.THREE,
        'FOUR': kvlclib.ChannelMask.FOUR,
        'FIVE': kvlclib.ChannelMask.FIVE,
    }
    
    # Iterate through each DBC file configuration and add them
    for dbc_config in config['dbc_files']:
        #path = os.path.join(gitpath, dbc_config['relativepath']) #does not work for some reason, probably beacause of \\

        path = gitpath + dbc_config['relativepath']

        channel_mask_str = dbc_config['channel_mask']
        
        if channel_mask_str not in channel_mask_mapping:
            raise ValueError(f"Invalid channel mask: {channel_mask_str}")
        
        channel_mask = channel_mask_mapping[channel_mask_str]
        kc.addDatabaseFile(path, channel_mask)

def try_set_property(converter, property, value=None):

    # Check if the format supports the given property
    if converter.format.isPropertySupported(property):
        # If a value is specified, set the property to this value
        if value is not None:
            converter.setProperty(property, value)

        # Get the property's default value
        default = converter.format.getPropertyDefault(property)
        #print(f'  {property} is supported (Default: {default})')

        # Get the property's current value
        value = converter.getProperty(property)
        #print(f'    Current value: {value}')
    #else:
        #print(f'  {property} is not supported')

def setconverter(config, folder_path, exportfilename, gitpath):

    # Set output format
    fmt = kvlclib.WriterFormat(kvlclib.FILE_FORMAT_MDF_4X_SIGNAL)

    print("Output format is '%s'" % fmt.name)
    
    # Set resulting output filename
    outfile = os.path.join(folder_path, exportfilename +"." + fmt.extension)
    print("Output filename is '%s'" % outfile)

    # Create converter
    kc = kvlclib.Converter(outfile, fmt)


    # Add DBC files from config file
    add_dbc_files_from_config(config, kc)

    # Set input filename and format
    
    kc.setInputFile(None ,file_format=kvlclib.FILE_FORMAT_MEMO_LOG)

    #Set File Properties:
    #https://kvaser.com/canlib-webhelp/kvlclib_8h.html#PROPERTY_xxx
    # Allow output file to overwrite existing files
    try_set_property(kc, kvlclib.PROPERTY_OVERWRITE, 1)
    try_set_property(kc, kvlclib.Property.COMPRESSION_LEVEL, 3)

    #try_set_property(kc, kvlclib.Property.FULLY_QUALIFIED_NAMES, 1)

    return kc
    # Convert all events

def converter(logs, location, config):
    inputfilename = config['inputfilename']
    ResultDir = config['resultDir']

    with kvmlib.openKmf(inputfilename) as kmf:
        for i, log_file in enumerate(kmf.log):

            if i not in logs:
                continue  # Skip this log file if its index is not in the logs list

            exportfilename = ('{start}_{location}_{duration}s'.
                format(start=log_file.start_time.strftime('%Y%m%d_%H%M%S'),
                        duration=int((log_file.end_time - log_file.start_time).total_seconds()),
                        location=location,))

            num=log_file.event_count_estimation()
            gitpath = config['gitpath']
            kc = setconverter(config, ResultDir, exportfilename, gitpath)

            #print("Saving to: %s" % kc.getOutputFilename())
            # The first logEvent contains device information
            event_iterator = iter(log_file)
            first_event = next(event_iterator)

            with alive_bar(num) as bar:
                
                #print(i)
                #print(first_event)
                kc.feedLogEvent(first_event)
                kc.convertEvent()

                for event in event_iterator:
                    kc.feedLogEvent(event)
                    #print(event)
                    kc.convertEvent()
                    bar()

                #for idx, event in enumerate(event_iterator, start=1):
                #    if idx > 4:  # Skip the first 4 events
                #        kc.feedLogEvent(event)
                #        #print(event)
                #        kc.convertEvent()
                #        bar()                    
                bar(num - bar.current)
            kc.flush()

#allfiles = range(0,283)

#file = [101, 140]
#
#gitpath = os.getcwd()
#
#converter(inputfilename, file, "Graz", ResultDir, config, gitpath)
