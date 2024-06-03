import yaml


from convertto_mf4 import convert_files_in_folder
from marple_api import uploadfiles



def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config("config.yml") #C:/config.yml
Filename = config['filename']
ResultDir = config['resultDir']
Locations = config['locations']

convert_files_in_folder(ResultDir, config)
print("Conversion complete, now uploading files to Marple...")
uploadfiles(ResultDir, "TEST", "Franz")