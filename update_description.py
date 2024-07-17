import os
import pickle
from googleapiclient.discovery import build  # Build Google API services
import config
from google.auth.transport.requests import Request  # Handle HTTP requests for authentication
from google_auth_oauthlib.flow import Flow,InstalledAppFlow  # Google OAuth library for authentication flow
from google.oauth2 import service_account
from google.cloud import storage as dns
import json
from termcolor import colored

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
                scopes = ['https://www.googleapis.com/auth/youtube','https://www.googleapis.com/auth/youtubepartner','https://www.googleapis.com/auth/youtube.force-ssl']

            )
            flow.run_local_server(port=8081, prompt='consent', authorization_prompt_message='')
            credentials = flow.credentials

            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)

    youtube = build("youtube", "v3", credentials=credentials)
    youtube_video_id=get_youtube_video_id(id_num)

    new_description=input("enter the new video description".format())

    # Get the current snippet of the video
    video_response = youtube.videos().list(
        part='snippet',
        id=youtube_video_id
    ).execute()

    video_snippet = video_response['items'][0]['snippet']
    video_title = video_snippet['title']

    # Define request body for video update
    request_body = {
        'id': youtube_video_id,
        'snippet': {
            'title': video_title,
            'description': new_description,
            'categoryId': video_snippet.get('categoryId', '22'),  # Default to '22' (People & Blogs) if categoryId is not present
            'tags': video_snippet.get('tags', [])
        }
    }

    response_update = youtube.videos().update(
        part='snippet',
        body=request_body
    ).execute()


    print(colored("         ****** Description updated successfully! ******","green", attrs=['bold']))
    print("check the video description on the above link")
    print("")

    return 0

    # return response_update
