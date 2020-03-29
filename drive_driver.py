import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
import json
import requests
import io

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.appdata',
    'https://www.googleapis.com/auth/drive.file'
]

class DriveDriver:
    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('drive_token.pickle'):
            with open('drive_token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('drive_token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)

    def uploadFile(self, name, pathToFile, mimetype=None):
        file_metadata = {'name': name}
        media = MediaFileUpload(pathToFile, mimetype=mimetype)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file['id']
    
    def uploadText(self, name, text, mimetype):
        file_metadata = {'name': name}
        media = MediaIoBaseUpload(io.StringIO(text), mimetype=mimetype)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file['id']

    def uploadFromURL(self, name, url, mimetype):
        response = requests.get(url)
        file_metadata = {'name': name}
        media = MediaIoBaseUpload(io.BytesIO(response.content), mimetype=mimetype)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file['id']