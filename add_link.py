# Import necessary libraries
import os
from google.oauth2 import service_account
from google.cloud import storage as dns
import json
import config

def add_link_to_metadata(id_num, id):

    """
    Adds a link to the metadata JSON file and uploads it to Google Cloud Storage.

    Args:
        id_num (str): The ID number associated with the video.
        id (str): The ID to be added to the metadata.

    Returns:
        None
    """
    
    # Get the current directory
    path = os.path.dirname(os.path.realpath(__file__))

    # Create a specific path for the metadata file
    path = os.path.join(path, id_num)
    local_json_file_path = os.path.join(path, "metadata.json")

    # Open the local JSON file for reading
    with open(local_json_file_path, 'r') as json_file:
        data = json.load(json_file)
        
        # Make changes to the data
        data['Upload IDs'] = {'Youtube': id}

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
