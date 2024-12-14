from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = './credentials/twstockgpt-ce9cb509f4fd.json'
CREDENTIALS = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SERVICE = build('drive', 'v3', credentials=CREDENTIALS)

def upload_to_google_drive(file_path, destination)
    media = MediaFileUpload(file_path)  # create the file object
    file = {'name': file_path, 'parents': [destination]}
    file_id = SERVICE.files().create(body=file, media_body=media).execute()
    print(file_id)
