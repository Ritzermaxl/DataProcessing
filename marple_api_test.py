import os
from dotenv import load_dotenv
from marple import Marple

load_dotenv()

ACCESS_TOKEN = os.getenv('SECRET_ACCESS_TOKEN')

m = Marple(ACCESS_TOKEN)

m.check_connection()
response = m.get('/version')
print(response.json()['message']) # 3.3.0

source_id = m.upload_data_file('./test_data/FSEAst_BrakeTest.mat',marple_folder="/test_folder")

