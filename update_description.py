import os
import pickle
from googleapiclient.discovery import build  # Build Google API services
import config
from google.auth.transport.requests import Request  # Handle HTTP requests for authentication
from google_auth_oauthlib.flow import Flow,InstalledAppFlow  # Google OAuth library for authentication flow
from google.oauth2 import service_account
from google.cloud import storage as dns
import json

# Youtube_Video_Id is the id which youtube assigns to our uploaded video
# Id_Number_Video is the our id of video which we use for naming uniquely

def get_youtube_video_id(id_num):
    """
    This function returns the youtube video id 
    
    Args:
        video_id(str): the ID of video locally or on google cloud storage  
    Returns:
        youtube id at which video is uploaded
    """

    # Get GCP key from configuration
    key = config.gcp_key

    # Create a GCP credentials object
    credential = service_account.Credentials.from_service_account_info(key)

    # Create a GCP storage client
    client = dns.Client(credentials=credential)

    # Get the GCP bucket
    bucket = client.get_bucket(config.gcp_bucket)

    # Define the filename in the bucket
    filename = config.gcp_path + str(id_num) + "/metadata.json"

    # Get the blob
    blob = bucket.blob(filename)

    # Download metadata JSON as text
    json_data = blob.download_as_text()

    # Load JSON data
    json_data = json.loads(json_data)

    # Check if "Upload IDs" key exists
    if "Upload IDs" in json_data.keys():
        # Check if "Youtube" key exists in "Upload IDs"
        if "Youtube" in json_data["Upload IDs"].keys():
            return json_data["Upload IDs"]["Youtube"]
    else:
        return ""



def update_description(id_num):
    """
    Updates the description of an existing YouTube video.

    Args:
        video_id (str): The ID of the video to update.
        new_description (str): The new description for the video.

    Returns:
        dict: The response from the YouTube API.
    """

    credentials = None

    if os.path.exists("token.pickle"):
        print('Loading Credentials From File...')
        with open("token.pickle", 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                config.yt_key_path,
                scopes = ['https://www.googleapis.com/auth/youtube.upload']
            )
            flow.run_local_server(port=8081, prompt='consent', authorization_prompt_message='')
            credentials = flow.credentials

            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)

    youtube = build("youtube", "v3", credentials=credentials)
    video_id=get_youtube_video_id(id_num)

    new_description=input("enter the new video description".format())

    # Define request body for video update
    request_body = {
        'id': video_id,
        'snippet': {
            'description': new_description,
        }
    }

    print("")
    print(video_id)
    print(id_num)
    print("")


    response_update = youtube.videos().update(
        part='snippet',
        body=request_body
    ).execute()

    print(response_update)

    print("Description updated successfully!")
    return 0

    # return response_update
