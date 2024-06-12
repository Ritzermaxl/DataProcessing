from converter import converter
#from marple_api import uploadfiles
import yaml
import os


def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        config['gitpath'] = os.getcwd()
    return config

config = load_config("config.yml") #C:/config.yml 

logstoexport = [3]
location = "Franz"
car = "tiffany"

converter(logstoexport, location, config)
#uploadfiles(config["resultDir"], location, car)