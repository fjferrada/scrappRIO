from __future__ import print_function
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import streamlit as st


def upload_to_google_drive(creds):
    """Uploads a file to a specific folder in Google Drive, overwriting if it exists."""

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

def download_from_google_drive(creds):
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