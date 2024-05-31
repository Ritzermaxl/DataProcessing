import glob
import os
import yaml
from InquirerPy import inquirer

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config("config.yml") #C:/config.yml
Filename = config['filename']
ResultDir = config['resultDir']
Locations = config['locations']

from convertto_km50 import listfiles
from convertto_km50 import downloadlogs

from convertto_mf4 import convert_files_in_folder

from marple_api import uploadfiles

def main():
    # Make sure the result directory exists and is empty 
    if os.path.isdir(ResultDir):
        files = glob.glob(os.path.join(ResultDir, "*"))
        for f in files:
            os.remove(f)
    else:
        os.mkdir(ResultDir)
    os.chdir(ResultDir)



    logstoexport = inquirer.checkbox(
        message="Select files to convert using [space], select all using [ALT+A]",
        choices=listfiles(Filename),
        validate=lambda result: len(result) >= 1,
        invalid_message="should be at least 1 selection",
    ).execute()

    car = inquirer.select(
        message="Select car",
        choices=config['cars'],
    ).execute()

    location = inquirer.select(
        message="Select location",
        choices=Locations,
    ).execute()

    downloadlogs(Filename, logstoexport, location)

    convert_files_in_folder(ResultDir, config)

    print("Conversion complete, now uploading files to Marple...")
    uploadfiles(ResultDir, location, car)


if __name__ == "__main__":
    main()