# 15_readResultFromSd.py
import glob
import os

from alive_progress import alive_bar

from canlib import EAN, VersionNumber
from canlib import kvmlib

# Our SD card is mounted under J:, so our LOG00000.KMF can
# be opened from here
filename = 'E:/LOG00000.KMF'

# Directory to put the resulting files in
resultDir = "result"

# Make sure the result directory exists and is empty
if os.path.isdir(resultDir):
    files = glob.glob(os.path.join(resultDir, "*"))
    for f in files:
        os.remove(f)
else:
    os.mkdir(resultDir)
os.chdir(resultDir)

# Open the SD card
# We have earlier verified that the SD card is using Lio Data Format v5.0
# and we should use kvmDEVICE_MHYDRA_EXT as the deviceType
with kvmlib.openKmf(filename) as kmf:
    ldf_version = kmf.log.ldf_version
    # Verify that the LIO data format of the card corresponds to
    # the device type we used when opening the device
    if ldf_version != VersionNumber(major=5, minor=0):
        if ldf_version == VersionNumber(major=3, minor=0):
            raise ValueError('This log file can be read if you reopen the'
                             ' device as kvmDEVICE_MHYDRA.')
        raise ValueError('Unexpected Lio Data Format: ' + str(ldf_version))

    # Read number of recorded logfiles
    num_log_files = len(kmf.log)
    print("Found {num} file on card: ".format(num=num_log_files))


    with alive_bar(num_log_files) as bar:

    # Loop through all logfiles and write their contents to .kme50 files
        for i, log_file in enumerate(kmf.log):
            print("\n==== File {index}: {start} - {end}, approx {num} events".
                format(index=i,
                        start=log_file.start_time,
                        end=log_file.end_time,
                        num=log_file.event_count_estimation()))
            # The first logEvent contains device information
            event_iterator = iter(log_file)
            first_event = next(event_iterator)
            ean = EAN.from_hilo([first_event.eanHi, first_event.eanLo])
            serial = first_event.serialNumber
            #Add EAN and serial number info to filename
            #logfile_name = ('log_{ean}_{sn}_{index:03}.kme50'.
            #               format(ean=str(ean), sn=serial, index=i))



            logfile_name = ('log_{start}_{end}_{index:03}.kme50'.
                format(start=log_file.start_time.strftime('%Y%m%d_%H%M%S'),
                        end=log_file.end_time.strftime('%Y%m%d_%H%M%S'),
                        index=i,))          

            print('Saving to:', logfile_name)
            with kvmlib.createKme(logfile_name) as kme:
                print(first_event)
                kme.write_event(first_event)
                for event in event_iterator:
                    # Write event to stdout
                    #print(event)
                    kme.write_event(event)
            bar()

    # Delete all logfiles
    # kmf.log.delete_all()