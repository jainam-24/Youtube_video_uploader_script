import Upload
import pandas as pd
from google.oauth2 import service_account
from google.cloud import storage as dns
import json
from download_video import download_json_files
import os
import shutil
import config
import get_title_and_description
from add_link import add_link_to_metadata
from termcolor import colored
import logging
from update_description import update_description
import time
import sys
from datetime import datetime
from datetime import date
from add_youtube_video_details_to_metadata import add_youtube_video_details_to_metadata

# Configure the logging settings
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def check_id_uploaded(id_num):
    """
    Checks if a video with the given ID has already been uploaded.

    Args:
        id_num (str): The ID number.

    Returns:
        bool: True if video is already uploaded, False otherwise.
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
        if "Youtube" in json_data['Upload IDs'].keys():
            id = json_data['Upload IDs']['Youtube']
            video_link = f'https://www.youtube.com/watch?v={id}'
            print("")
            print(colored("Video already uploaded before! Video link: " + video_link, "green", attrs=['bold']))
            print("")
            return True
        else:
            return False
    else:
        return False

# Loop for user interaction
while(True):


    logging.debug('Starting main loop iteration')
    print("Welcome to Youtube video uploading script :")
    print("Select a option")
    print("1. Upload video from PC")
    logging.debug('Displaying menu option: Upload video from PC')

    print("2. Fetch IDs from CSV")
    logging.debug('Displaying menu option: Fetch IDs from CSV')

    print("3. Fetch IDs from Database")
    logging.debug('Displaying menu option: Fetch IDs from Database')

    print("4. Update description of existing video on YouTube: ")
    logging.debug('Displaying menu option: Update description of existing video')

    print("5. Exit")
    logging.debug('Displaying menu option: Exit')    
    print("")

    logging.debug('Prompting user for choice')
    c = int(input())
    logging.debug(f'User entered choice: {c}')
    print("")
    if (c==1):
        # Option 1 - Upload video from PC
        print("Enter video path")
        logging.debug("Enter video path")
        video_path = input()
        logging.debug(f"User input: {video_path}")

        print("Enter thumbnail path")
        logging.debug("Enter thumbnail path")
        thumbnail_path = input()
        logging.debug(f"User input: {thumbnail_path}")

        print("Enter video title")
        logging.debug("Enter video title")
        title = input()
        logging.debug(f"User input: {title}")


        print("Enter video description")
        logging.debug("Enter video description")
        description = input()
        logging.debug(f"User input: {description}")


        future_publishing=input("Do you want to publish video in future? y:n => ")
        
        if future_publishing=="Y" or future_publishing=="y":
            print("Enter date on which video should be uploaded")
            print("Enter date in YYYY-MM-DD format:")
            logging.debug("Prompting user for date input")
            date_input = input()
            logging.debug(f"User input (date): {date_input}")
            yyyy, mm, dd = date_input.split('-')

            print("Enter time on which video should be uploaded in format (HH-MM-SS)")
            # print("Enter time in HH:MM:SS format:")
            logging.debug("Prompting user for time input")
            time_input = input()
            logging.debug(f"User input (time): {time_input}")

            # Split the time input into hour, minute, and second
            HH, MM, SS = time_input.split('-')
        
        else:
            now = datetime.now()
            current_time = str(now.strftime("%H:%M:%S"))
            current_date=str(date.today())
            yyyy,mm,dd=current_date.split('-')
            HH,MM,SS=current_time.split(':')
                
        # Upload the video using the provided information
        
        
        video_link = Upload.Upload().upload(yyyy,mm,dd,HH,MM,SS,title,description,video_path,thumbnail_path)
        # print("this flow is completed")

    elif(c==2):
        
		# Option 2: Fetch IDs from CSV
        logging.debug('User selected option 2: Fetch IDs from CSV')
        print("Enter CSV path")
        logging.debug('Prompting user for CSV path')
        csv_path = input()
        logging.debug(f'User entered CSV path: {csv_path}')

        # Read CSV file
        if ".csv" in csv_path:
            df = pd.read_csv(csv_path)
        else:
            df = pd.read_excel(csv_path)
        
        # Get all headers of csv
        headers = list(df.columns)
        j=1
        print("")
        for i in headers:
            print(str(j) + ". " + i)
            j+=1
        # Ask user to select the header containing IDs
        print("")
        logging.debug('Displayed headers for user selection')
        print("Enter the index of the column containing the IDs")
        logging.debug('Prompting user for index of IDs column')
        index = int(input())
        logging.debug(f'User entered index: {index}')

        # Get all IDs
        ids = df[headers[index-1]].dropna().tolist()

        # Ask user if any prefix is to be added
        ch = int(input("Enter 1 to add prefix to all IDS: "))
        logging.debug(f'Prompting user for prefix addition choice: {ch}')
        if(ch==1):
            prefix = input("Enter prefix: ")
            for i in range(len(ids)):
                ids[i] = prefix + str(ids[i])

        logging.debug('Processed IDs')
        print("IDs found:" + str(len(ids)))
        print(ids)

        future_publishing=input("Do you want to publish video in future? y:n => ")
        
        if future_publishing=="Y" or future_publishing=="y":
            print("Enter date on which video should be uploaded")
            print("Enter date in YYYY-MM-DD format:")
            logging.debug("Prompting user for date input")
            date_input = input()
            logging.debug(f"User input (date): {date_input}")
            yyyy, mm, dd = date_input.split('-')

            print("Enter time on which video should be uploaded in format (HH-MM-SS)")
            # print("Enter time in HH:MM:SS format:")
            logging.debug("Prompting user for time input")
            time_input = input()
            logging.debug(f"User input (time): {time_input}")

            # Split the time input into hour, minute, and second
            HH, MM, SS = time_input.split('-')
        
        else:
            now = datetime.now()
            current_time = str(now.strftime("%H:%M:%S"))
            current_date=str(date.today())
            yyyy,mm,dd=current_date.split('-')
            HH,MM,SS=current_time.split(':')

                

        # Looping through each ID
        for i in ids:
            logging.debug(f'Processing ID: {i}')
            # Check if Id already uploaded
            choice = check_id_uploaded(i)
                
            if choice==False:
            # Get Title and Description
                # title, description = get_title_and_description.get(i)
                title, description = "First","sample"
                # Get Videos
                download_json_files(i)
                video_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), i),config.video_with_music_filename)
                thumbnail_path = ""
                # Upload Video to Youtube
                
                video_id = Upload.Upload().upload(yyyy,mm,dd,HH,MM,SS,title,description,video_path,thumbnail_path)
                
                logging.debug(f'Video uploaded for ID: {i}')
                # Add Link to Metadata
                add_link_to_metadata(i,video_id)
                logging.debug(f'Link added to metadata for ID: {i}')
                # Remove temp files
                shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) +  "/" + i)
                logging.debug(f'Removed temp directory for ID: {i}')
                logging.debug(f'Successfully Uploaded ID: {i}')
            else:
                logging.debug(f'ID already uploaded: {i}')
			

    elif(c==3):		
	    # Option 3: Fetch IDs from Database
        logging.debug('User selected option 3: Fetch IDs from Database')

        # Ask for prefix
        print("Enter prefix to fetch IDs from Database")
        logging.debug('Prompting user for prefix')
        prefix = input()
        logging.debug(f'User entered prefix: {prefix}')

        # Retrieve GCP credentials and initialize the client and bucket
        key=config.gcp_key
        credential = service_account.Credentials.from_service_account_info(key)
        client = dns.Client(credentials=credential)
        bucket = client.get_bucket(config.gcp_bucket)

        # Find IDs with the given prefix
        pre = config.gcp_path + prefix
        # blobs = list(bucket.list(pre, "/"))
        blobs = bucket.list_blobs(prefix=pre)
        ids = []
        for blob in blobs:
            start = '/'
            end = '/'
            s = blob.name
            s = (s.split(start))[1].split(end)[0]        
            ids.append(s)
        ids = list(set(ids))
        print("")
        logging.debug(f'Number of IDs found: {len(ids)}')
        print("IDs found:" + str(len(ids)))
        print(ids)
        print("")

        future_publishing=input("Do you want to publish video in future? y:n => ")
        
        if future_publishing=="Y" or future_publishing=="y":
            print("Enter date on which video should be uploaded")
            print("Enter date in YYYY-MM-DD format:")
            logging.debug("Prompting user for date input")
            date_input = input()
            logging.debug(f"User input (date): {date_input}")
            yyyy, mm, dd = date_input.split('-')

            print("Enter time on which video should be uploaded in format (HH-MM-SS)")
            # print("Enter time in HH:MM:SS format:")
            logging.debug("Prompting user for time input")
            time_input = input()
            logging.debug(f"User input (time): {time_input}")

            # Split the time input into hour, minute, and second
            HH, MM, SS = time_input.split('-')
        
        else:
            now = datetime.now()
            current_time = str(now.strftime("%H:%M:%S"))
            current_date=str(date.today())
            yyyy,mm,dd=current_date.split('-')
            HH,MM,SS=current_time.split(':')



        print("")
        print("loading...")
        print("")

        # Looping through each ID
        for i in ids:
             
            logging.debug(f'Processing ID: {i}')
            # Check if Id already uploaded
            choice = check_id_uploaded(i)
            if choice==False:
                # Get Title and Description
                # title, description = get_title_and_description.get(i)
                title, description = "video for test","sample description"
                # Get Videos
                download_json_files(i)
                video_path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), i),config.video_with_music_filename)
                thumbnail_path = ""
                # Upload Video to Youtube
                video_id = Upload.Upload().upload(yyyy,mm,dd,HH,MM,SS,title,description,video_path,thumbnail_path)
                logging.debug(f'Video uploaded for ID: {i}')
                # Add Link to Metadata
                add_link_to_metadata(i,video_id)
                logging.debug(f'Link added to metadata for ID: {i}')

                # add_youtube_video_details_to_metadata(i,title,description,yyyy,mm,dd,HH,MM,SS)
                
                # Remove temp files
                shutil.rmtree(os.path.dirname(os.path.realpath(__file__)) +  "/" + i)
                logging.debug(f'Removed temp directory for ID: {i}')
                logging.debug(f'Successfully Uploaded ID: {i}')
            else:
                logging.debug(f'ID already uploaded: {i}')
            

    elif(c==4):
        logging.debug("user selected option 4: update video description")
        print("Enter prefix to fetch IDs from Database")
        logging.debug('Prompting user for prefix')
        prefix = input()
        logging.debug(f'User entered prefix: {prefix}')

        # Retrieve GCP credentials and initialize the client and bucket
        key=config.gcp_key
        credential = service_account.Credentials.from_service_account_info(key)
        client = dns.Client(credentials=credential)
        bucket = client.get_bucket(config.gcp_bucket)

        # Find IDs with the given prefix
        pre = config.gcp_path + prefix
        # blobs = list(bucket.list(pre, "/"))
        blobs = bucket.list_blobs(prefix=pre)
        ids = []
        for blob in blobs:
            start = '/'
            end = '/'
            s = blob.name
            s = (s.split(start))[1].split(end)[0]        
            ids.append(s)
        ids = list(set(ids))
        print("")
        logging.debug(f'Number of IDs found: {len(ids)}')
        print("IDs found:" + str(len(ids)))
        print(ids)
        print("")

        for i in ids:
            video_exist=check_id_uploaded(i)
            if not video_exist:
                print("Video does not exist for id {} on youtube, upload the video first".format(i))
                print("")
            else:
                update_description(i)    
    elif(c==5):
        # Exit option
        logging.debug('User selected option 5: Exit')
        break

    else:
        # Invalid choice
        print("Please enter a valid choice")
        print("")
        logging.debug('User entered an invalid choice')
