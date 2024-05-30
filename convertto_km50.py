import glob
import os
from alive_progress import alive_bar
from canlib import EAN, VersionNumber
from InquirerPy.base.control import Choice
from canlib import kvmlib
import yaml

def listfiles(filename):
    with kvmlib.openKmf(filename) as kmf:

        ldf_version = kmf.log.ldf_version
        if ldf_version != VersionNumber(major=5, minor=0):
            if ldf_version == VersionNumber(major=3, minor=0):
                raise ValueError('This log file can be read if you reopen the'
                                ' device as kvmDEVICE_MHYDRA.')
            raise ValueError('Unexpected Lio Data Format: ' + str(ldf_version))
        
        num_log_files = len(kmf.log)
        filelist = []
        for i, log_file in enumerate(kmf.log):
            name = "File {index}: {start} - {end}, approx {num} events.".format(
                index=i,
                start=log_file.start_time,
                end=log_file.end_time,
                num=log_file.event_count_estimation()
            )
            filelist.append(Choice(i, name))

    return filelist

def downloadlogs(filename, logs, ResultDir, config):
    with kvmlib.openKmf(filename) as kmf:
        for i, log_file in enumerate(kmf.log):
            if i not in logs:
                continue  # Skip this log file if its index is not in the logs list
            
            num=len(list(log_file))
            # The first logEvent contains device information
            event_iterator = iter(log_file)
            first_event = next(event_iterator)
            logfile_name = ('{start}_{duration}s_{index:03}.kme50'.
                format(start=log_file.start_time.strftime('%Y%m%d_%H%M%S'),
                        duration=int((log_file.end_time - log_file.start_time).total_seconds()),
                        index=i,))          
            print('Saving to:', logfile_name)

            with alive_bar(num-1) as bar:
                with kvmlib.createKme(logfile_name) as kme:
                    print(first_event)
                    kme.write_event(first_event)
                    for event in event_iterator:
                        # Write event to stdout
                        #print(event)
                        kme.write_event(event)
                        bar()