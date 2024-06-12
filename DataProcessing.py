import glob
import os
import yaml
from InquirerPy import inquirer

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        config['gitpath'] = os.getcwd()
    return config

config = load_config("config.yml") #C:/config.yml 


from marple_api import uploadfiles
from converter import converter, listfiles
from checkdbcfiles import check_submodule_status, update_submodule

def clearResultDir(config):
    ResultDir = config['resultDir']
    if os.path.isdir(ResultDir):
        files = glob.glob(os.path.join(ResultDir, "*"))
        for f in files:
            os.remove(f)
            continue
    else:
        os.mkdir(ResultDir)  

def main():

    repo_path = os.getcwd()
    submodule_path = "CanNetworks2024"
    print("Checking if DBC files are up to date...")
    is_up_to_date = check_submodule_status(repo_path, submodule_path)

    if not is_up_to_date:
        update = False
        update = inquirer.confirm(message=f"Do you want to update the submodule at {submodule_path}?", default=True).execute()
        if update:
            update_submodule(repo_path, submodule_path)

    clearResultDir(config)

    logstoexport = inquirer.checkbox(
        message="Select files to convert using [space], select all using [ALT+A]",
        choices=listfiles(config),
        validate=lambda result: len(result) >= 1,
        invalid_message="should be at least 1 selection",
    ).execute()

    car = inquirer.select(
        message="Select car",
        choices=config['cars'],
    ).execute()

    location = inquirer.select(
        message="Select location",
        choices=config['locations'],
    ).execute()

    converter(logstoexport, location, config)

    print("Conversion complete, now uploading files to Marple...")
    uploadfiles(config["resultDir"], location, car)


if __name__ == "__main__":
    main()