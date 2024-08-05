import datetime  # Module for working with dates and times
from Google import Create_Service  # Custom module for creating a Google API service
import os  # Operating System functions
from googleapiclient.http import MediaFileUpload  # Handle media file uploads
from google.auth.transport.requests import Request  # Handle HTTP requests for authentication
from google_auth_oauthlib.flow import Flow,InstalledAppFlow  # Google OAuth library for authentication flow
from googleapiclient.discovery import build  # Build Google API services
import pickle  # Module for serializing and deserializing Python objects
from termcolor import colored  # Terminal color output
import pytz  # Python timezone support
import config

class Upload():

    def convert_ist_to_utc(self, ist_datetime):
        """
        Convert IST (Indian Standard Time) to UTC (Coordinated Universal Time).
        Args:
            ist_datetime (datetime): Datetime in IST.
        Returns:
            datetime: Datetime in UTC.
        """
        # Define timezone objects for IST and UTC
        ist_tz = pytz.timezone('Asia/Kolkata')
        utc_tz = pytz.timezone('UTC')

        # Convert the input datetime object to the IST timezone
        ist_datetime = ist_tz.localize(ist_datetime)

        # Convert the datetime object to the UTC timezone
        utc_datetime = ist_datetime.astimezone(utc_tz).replace(tzinfo=None)
        return utc_datetime

    def upload(self, yyyy, mm, dd, HH, MM, SS, title, description, video_path, thumbnail_path):

        """
        Uploads a video to YouTube.

        Args:
            yyyy (str): Year.
            mm (str): Month.
            dd (str): Day.
            HH (str): Hour.
            MM (str): Minute.
            SS (str): Second.
            title (str): Title of the video.
            description (str): Description of the video.
            video_path (str): Path to the video file.
            thumbnail_path (str): Path to the thumbnail image file.

        Returns:
            str: Video ID.
        """

        credentials = None

        if os.path.exists("token.pickle"):
            print('Loading Credentials From File...')
            with open("token.pickle", 'rb') as token:
                credentials = pickle.load(token)

        # If there are no valid credentials available, then either refresh the token or log in.
        if not credentials or not credentials.valid:

            if credentials and credentials.expired and credentials.refresh_token:

                print('Refreshing Access Token...')
                credentials.refresh(Request())
            else:

                print('Fetching New Tokens...')

                flow = InstalledAppFlow.from_client_secrets_file(
                    config.yt_key_path,
                    scopes = ['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtubepartner']
                )
                
                #'https://www.googleapis.com/auth/youtubepartner',
                #'https://www.googleapis.com/auth/youtube',
                #'https://www.googleapis.com/auth/youtube.force-ssl'
                
                flow.run_local_server(port=8081, prompt='consent',
                                      authorization_prompt_message='')
                credentials = flow.credentials

                # Save the credentials for the next run
                with open('token.pickle', 'wb') as f:
                    print('Saving Credentials for Future Use...')
                    pickle.dump(credentials, f)

        youtube = build("youtube", "v3", credentials = credentials)

        # Convert provided date and time to RFC3339 format
        upload_date_time = self.convert_ist_to_utc(datetime.datetime(int(yyyy), int(mm), int(dd), int(HH), int(MM),
                                                                     int(SS))).isoformat() + '.000Z'

        # Define request body for video upload
        request_body = {
            'snippet': {
                'title': title,
                'description': description
            },
            'status': {
                'privacyStatus': 'private',
                'publishAt': upload_date_time
            }
        }

        # Upload video using MediaFileUpload
        mediaFile = MediaFileUpload(video_path)

        response_upload = youtube.videos().insert(
            part='snippet,status',
            body=request_body,
            media_body=mediaFile
            ).execute()

        # If a thumbnail path is provided, set the thumbnail for the video
        if thumbnail_path != "":
            youtube.thumbnails().set(
                videoId=response_upload.get('id'),
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()

        video_id = response_upload['id']
        video_link = f'https://www.youtube.com/watch?v={video_id}'

        # print("")
        # print(colored("Video uploaded successfully! Video link: " + video_link, 'green', attrs=['bold']))
        # print("")

        print("")
        message = colored("Video uploaded successfully! Video link: ","magenta") + colored('\033[4m'+video_link+'\033[0m', 'green', attrs=['bold'])
        print(message)
        print("")
        return video_id


        if thumbnail_path!="":

            youtube.thumbnails().set(
                videoId=response_upload.get('id'),
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()

        video_id = response_upload['id']
        video_link = f'https://www.youtube.com/watch?v={video_id}'
        print("")
        print(colored("Video uploaded successfully! Video link: " + video_link, 'green', attrs=['bold']))
        # print("\033[1;32m" + "\033[1;37m" + "Video uploaded successfully! Video link: " + video_link + "\033[0m")
        print("")
        # print("Video Uploaded Successfully")

        return video_id