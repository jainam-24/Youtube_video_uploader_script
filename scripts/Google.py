import pickle  # Module for serializing and deserializing Python objects
import os  # Operating System functions
from google_auth_oauthlib.flow import Flow, InstalledAppFlow  # Google OAuth library for authentication flow
from googleapiclient.discovery import build  # Build Google API services
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload  # Handling media uploads and downloads
from google.auth.transport.requests import Request  # Handle HTTP requests
import datetime

def Create_Service(client_secret_file, api_name, api_version, *scopes):
    """
    Creates a Google API service.

    Args:
        client_secret_file (str): The client secret file for authentication.
        api_name (str): The name of the API.
        api_version (str): The version of the API.
        *scopes: Variable number of API scopes.
        
    Returns:
        service: The created Google API service.
    """
    
    print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    print(SCOPES)

    cred = None

    # Create a token file name
    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'

    # Check if token file exists, and load credentials if it does
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    # If credentials are not valid or don't exist, authenticate and create token
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        # Save the new credentials to the token file
        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        # Build the service with the provided credentials
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None


def convert_to_RFC_datetime(year, month, day, hour, minute):
    """
    Converts date and time to RFC3339 format.

    Args:
        year (int): Year.
        month (int): Month.
        day (int): Day.
        hour (int): Hour.
        minute (int): Minute.

    Returns:
        str: Date and time in RFC3339 format.
    """
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt
