import os
from dotenv import load_dotenv
from marple import Marple
import yaml
import json

load_dotenv()

ACCESS_TOKEN = os.getenv('SECRET_ACCESS_TOKEN')

m = Marple(ACCESS_TOKEN)

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config("config.yml") #C:/config.yml
Filename = config['filename']
ResultDir = config['resultDir']
Locations = config['locations']

m.check_connection()
response = m.get('/version')
print(response.json()['message']) # 3.3.0

def listremotefolder(folder_name):

    response = m.get('/library/folder/contents',params={'path': folder_name})
    foldercontent = json.loads(response.text)
    remotefilelist = [item['label'] for item in foldercontent['message']]
    
    
    print(remotefilelist)
    return remotefilelist

def listlocalfolder(ResultDir):

    localfilelist = [f for f in os.listdir(ResultDir)]

    return localfilelist



def marplefolder(ResultDir, Location):

    LocalFiles = listlocalfolder(ResultDir)

    RemoteFolderName = LocalFiles[0][:8]+"_"+Location

    print(RemoteFolderName)

    #listremotefolder(RemoteFolderName)
    #MarpleFiles = listremotefolder("VSM Results")


marplefolder(ResultDir, "Office")


print(listremotefolder(""))



#check_folder("VSM Results")

# json={'path': "/test_folder"}