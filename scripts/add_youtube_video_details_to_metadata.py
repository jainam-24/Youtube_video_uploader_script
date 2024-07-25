# Import necessary libraries
import os
from google.oauth2 import service_account
from google.cloud import storage as dns
import json
import config
import datetime


def add_youtube_video_details_to_metadata(id_num,title,description,yyyy,mm,dd,HH,MM,SS):
    # Get the current directory
    path = os.path.dirname(os.path.realpath(__file__))

    # Create a specific path for the metadata file
    path = os.path.join(path, id_num)
    local_json_file_path = os.path.join(path, "metadata.json")

    # Open the local JSON file for reading
    with open(local_json_file_path, 'r') as json_file:
        data = json.load(json_file)
        
        # Make changes to the data
        # Create a datetime object for accurate formatting
        date_time = datetime.datetime(year=yyyy, month=mm, day=dd, hour=HH, minute=MM, second=SS)

        # Format the datetime object in the desired format (YYYY-MM-DD HH:MM:SS)
        formatted_date_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
        data['Youtube_Video_Details'] = {'Video_title': title,'Video_description':description,
                                         'upload_date_time':formatted_date_time}

    # Write the updated data back to the local JSON file
    with open(local_json_file_path, 'w') as json_file:
        json.dump(data, json_file)

    # Get GCP key from configuration
    key = config.gcp_key

    # Create a GCP credentials object
    credential = service_account.Credentials.from_service_account_info(key)

    # Create a GCP storage client
    client = dns.Client(credentials=credential)

    # Get the GCP bucket
    bucket = client.get_bucket(config.gcp_bucket)

    # Define the path for the blob
    pre = config.gcp_path + str(id_num) + "/" + "metadata.json"

    # Create a blob object
    blob = bucket.blob(pre)

    # Upload the local JSON file to GCP storage
    blob.upload_from_filename(local_json_file_path)
