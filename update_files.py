from __future__ import print_function
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import streamlit as st


def upload_to_google_drive():
    """Uploads a file to a specific folder in Google Drive, overwriting if it exists."""
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = None
    # Use Streamlit secrets to get credentials
    client_id = st.secrets["google"]["client_id"]
    client_secret = st.secrets["google"]["client_secret"]
    redirect_uris = st.secrets["google"]["redirect_uris"]

    # Create a credentials.json-like structure
    credentials_info = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": redirect_uris
        }
    }

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                credentials_info, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # File to upload
        folder_id = '182g1HptziJLobSb4hcNOTUGKqPLwrOuY'  # Replace with your actual folder ID
        file_name = 'registro.csv'

        # Search for the file in the specified folder
        query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        # If the file exists, delete it
        if items:
            for item in items:
                print(f"Deleting existing file: {item['name']} (ID: {item['id']})")
                service.files().delete(fileId=item['id']).execute()

        # Upload the new file
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload('data/registro.csv', mimetype='text/csv')
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File uploaded successfully. File ID: {file.get('id')}")

    except Exception as e:
        print(f"An error occurred: {e}")

def download_from_google_drive():
    """Downloads 'registro.csv' from a specific folder in Google Drive."""
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = None
    # Use Streamlit secrets to get credentials
    client_id = st.secrets["google"]["client_id"]
    client_secret = st.secrets["google"]["client_secret"]
    redirect_uris = st.secrets["google"]["redirect_uris"]

    # Create a credentials.json-like structure
    credentials_info = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": redirect_uris
        }
    }

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                credentials_info, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # File to download
        folder_id = '182g1HptziJLobSb4hcNOTUGKqPLwrOuY'  # Replace with your actual folder ID
        file_name = 'registro.csv'

        # Search for the file in the specified folder
        query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        # If the file exists, download it
        if items:
            file_id = items[0]['id']
            request = service.files().get_media(fileId=file_id)
            file_path = os.path.join('data', file_name)  # Ensure the directory exists
            with open(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%.")

            print(f"File downloaded successfully to {file_path}")
        else:
            print(f"File '{file_name}' not found in the specified folder.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # upload_to_google_drive()
    download_from_google_drive()