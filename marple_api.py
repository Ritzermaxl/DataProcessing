import os
from dotenv import load_dotenv
from marple import Marple
import yaml
import json
import shutil

load_dotenv()

ACCESS_TOKEN = os.getenv('SECRET_ACCESS_TOKEN')

m = Marple(ACCESS_TOKEN)

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

config = load_config("config.yml") #C:/config.yml
ResultDir = config['resultDir']
Locations = config['locations']
ArchiveDir = config['archiveDir']


m.check_connection()
response = m.get('/version')
#print(response.json()['message']) # 3.3.0

def listremotefolder(folder_name):
    #Probably not needed anymore
    response = m.get('/library/folder/contents',params={'path': folder_name})
    foldercontent = json.loads(response.text)
    remotefilelist = [item['label'] for item in foldercontent['message']]
    
    
    #print(remotefilelist)
    return remotefilelist

def listlocalfolder(ResultDir):

    localfilelist = [f for f in os.listdir(ResultDir)]

    return localfilelist

def remotefoldername(ResultDir, Location):
    
    LocalFiles = listlocalfolder(ResultDir)
    RemoteFolderName = LocalFiles[0][:8]+"_"+Location

    return RemoteFolderName

def uploadmarplefile(ResultDir, File, Location, Car):

    inputFile = os.path.join(ResultDir, File)

    RemoteFolderName = remotefoldername(ResultDir, Location)

    if inputFile not in listremotefolder(RemoteFolderName):

        source_id = m.upload_data_file(inputFile, "/"+Car+"/"+RemoteFolderName, metadata={'Car': Car, 'Location': Location})
        print("Uploaded file: %s" % inputFile)
        #Car+"/"+RemoteFolderName

    else:
        return None

    return RemoteFolderName

def uploadfiles(ResultDir, Location, Car):

    files = [f for f in os.listdir(ResultDir) if os.path.isfile(os.path.join(ResultDir, f)) and f.lower().endswith(('.mf4', '.mat', '.mdf'))]
    
    for file in files:
        try:
            RemoteFolderName = uploadmarplefile(ResultDir, file, Location, Car)
            #os.remove(os.path.join(ResultDir, file))

            if RemoteFolderName:  # Check if the file was uploaded and RemoteFolderName was returned
                # Define the archive path
                archivePath = os.path.join(ArchiveDir, RemoteFolderName)
                # Create the directory if it doesn't exist
                if not os.path.exists(archivePath):
                    os.makedirs(archivePath)
                # Move the file
                shutil.move(os.path.join(ResultDir, file), os.path.join(archivePath, file))
                print(f"Moved {file} to archive folder: {archivePath}")

        except Exception as e:
            print(f"Error occurred while uploading {file}: {e}") 


#uploadmarplefiles(ResultDir, "20240415_105741_64s_002.mf4", "Office", "TestCar")
