import os
from google.oauth2 import service_account
from google.cloud import storage as dns
import json
import cv2
import shutil
import base64
import io
from io import BytesIO
from base64 import b64encode
from Crypto.Cipher import AES
import numpy as np
import config
from moviepy.editor import ImageSequenceClip
from moviepy.editor import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import random
import logging

# Configure the logging settings
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def check_video_exists(id_num):

    """
    This function checks if video files exist in the specified Google Cloud
    Storage bucket for a given id_num. It uses Google Cloud Storage API to check
    if the video and video with music files exist. It returns 0 if neither exist,
    1 if only the video exists, and 2 if both video and video with music exist.

    Args:
        id_num (str): A unique identifier for the video.

    Returns:
        int: 0 if neither video exists, 1 if only the original video exists, and 2 if both video and video with music exist.

    """

    logging.debug(f'Checking if video exists for id_num: {id_num}')

    # Get the Google Cloud Platform (GCP) key from the configuration
    key = config.gcp_key
    
    # Create a credential object using the GCP key
    credential = service_account.Credentials.from_service_account_info(key)
    
    # Initialize a client to interact with Google Cloud Storage
    client = dns.Client(credentials=credential)
    
    # Get the bucket named 'd360us'
    bucket = client.get_bucket(config.gcp_bucket)
    
    # Define file paths for the original video and video with music
    filename = config.gcp_path + str(id_num) + "/"  + config.video_filename
    filename_with_music = config.gcp_path + str(id_num) + "/" + config.video_with_music_filename
    
    # Get information about whether the original video exists in the bucket
    blob = bucket.blob(filename)
    video_exists = blob.exists()
    
    # Get information about whether the video with music exists in the bucket
    blob1 = bucket.blob(filename_with_music)
    video_with_music_exists = blob1.exists()
    
    # Return codes:
    # 0 - Video doesn't exist
    # 1 - Only original video exists
    # 2 - Video with music exists
    if video_with_music_exists:
        return 2
    elif video_exists:
        return 1
    else:
        return 0


def download_json_files(id_num):


    """
    This function downloads JSON files from the Google Cloud Storage bucket based on
    the id_num. It first creates a local directory with the id_num as the name. Then, 
    it uses the check_video_exists function to determine which files to download. 
    It downloads either the metadata and video, or metadata and video with music.

    Args:
        id_num (str): A unique identifier for the video.

    Returns:
        None

    """

    logging.debug(f'Downloading JSON files for id_num: {id_num}')

    # Get the current file path
    path = os.path.dirname(os.path.realpath(__file__))
    
    # Combine the file path with the provided id_num
    path = os.path.join(path, id_num)
    
    # Create the directory if it doesn't exist
    if not os.path.exists(path):
        os.mkdir(path)
        
    # Check if the video exists and get choice value (0, 1, or 2)
    choice = check_video_exists(id_num)
    
    # Retrieve GCP credentials and initialize the client and bucket
    key = config.gcp_key
    credential = service_account.Credentials.from_service_account_info(key)
    client = dns.Client(credentials=credential)
    bucket = client.get_bucket(config.gcp_bucket)
    
    # Process based on the choice value
    if choice == 0:

        logging.debug(f'Only metadata and json files exists for id_num: {id_num}')

        # List of files to download if only metadata and json files exist
        files = ['metadata.json', '0.json', '1.json', '2.json', '3.json', '4.json', '5.json', '6.json', '7.json',
                 '8.json', '9.json', '10.json']
        
        # Download each file from the GCP bucket
        for i in files:
            pre = config.gcp_path + str(id_num) + "/" + i
            blobs = bucket.list_blobs(prefix=pre)
            for blob in blobs:
                blob.download_to_filename(os.path.join(path, i))
                
        # Process the downloaded JSON files
        json_to_dict(path, id_num)
        
    elif choice == 1:

        logging.debug(f'Video file exists for id_num: {id_num}')

        # List of files to download if video file exists
        files = ['metadata.json', config.video_filename]
        
        # Download each file from the GCP bucket
        for i in files:
            pre = config.gcp_path + str(id_num) + "/" + i 
            blobs = bucket.list_blobs(prefix=pre)
            for blob in blobs:
                blob.download_to_filename(os.path.join(path, i))
                
        # Process the downloaded video file (add music)
        add_music_to_video(os.path.join(path, config.video_filename), id_num)
        
    elif choice == 2:

        logging.debug(f'Video with music file exists for id_num: {id_num}')

        # List of files to download if video with music file exists
        files = ['metadata.json', config.video_with_music_filename]
        
        # Download each file from the GCP bucket
        for i in files:
            pre = config.gcp_path + str(id_num) + "/" + i 
            blobs = bucket.list_blobs(prefix=pre)
            for blob in blobs:
                blob.download_to_filename(os.path.join(path, i))


def json_to_dict(folder_path, id_num):

    """
    This function processes JSON files in the specified folder to create an image dictionary. 
    It expects atleast three JSON files ('1.json', '2.json', '3.json') to be present. It also 
    uses the functions decodingScramble, makingMappingDict, and extract_images in its process.

    Args:
        folder_path (str): The path to the folder containing JSON files.
        id_num (str): A unique identifier for the video.

    Returns:
        None

    """
    
    logging.debug(f'Converting JSON files to dictionary for id_num: {id_num}')
    
    # Define a set of required JSON files
    required = set(['1.json', '2.json', '3.json'])
    count = 0
    num_json = 0
    
    # Traverse through the files and subdirectories in the given folder path
    for local_file, subdirs, files in os.walk(folder_path):
        # Check if the required JSON files are present in the current directory
        if required.issubset(set(files)):
            for f in files:
                # Check if the file is a JSON file and its prefix is a valid number
                if f.split('.')[-1] == 'json' and f.split('.')[0] in ['0', '1', '2', '3', '4', '5', '6', '7',
                                                                      '8', '9', '10']:
                    num_json += 1
            
            try:
                # Decode the scramble and get a mapping
                mapping_scramble = decodingScramble(local_file)
            except Exception as e:
                print(e)
                mapping_scramble = {}

            # Create a mapping dictionary based on the number of JSON files
            mappingx = makingMappingDict(num_json)
            
            # Update the mapping if a scramble mapping is available
            if mapping_scramble:
                for i, j in mapping_scramble.items():
                    mapping_scramble[i] = int(mappingx[j])
                mappingx = mapping_scramble
                
            # Extract images using the mapping
            image_dict = extract_images(local_file, mappingx, num_json)
            total_images = len(image_dict)
            
    # Write the images to an MP4 file
    mp4Writer(id_num, num_json, image_dict)





def makingMappingDict(num_json):

    """
    This function generates a mapping dictionary used for processing JSON files. It 
    assigns a unique value to each image based on its position.

    Args:
        num_json (int): The number of JSON files available.

    Returns:
        dict: A mapping dictionary used for processing JSON files.

    """

    logging.debug(f'Creating mapping dictionary for num_json: {num_json}')


    # Calculate the total number of mappings possible
    total = pow(2, num_json)
    
    # Initialize an empty mapping dictionary
    mappingx = {}
    
    # Set initial mappings (1, 2, 3, 4) for the first four indices
    mappingx[1] = 1
    mappingx[2] = (total // 4) + 1
    mappingx[3] = (total // 4) * 2 + 1
    mappingx[4] = (total // 4) * 3 + 1
    
    # Initialize denominator and start value for mappings
    denominator = 4
    x = 5
    
    # Loop through to calculate mappings for remaining indices
    for i in range(num_json - 2):
        denominator *= 2
        for j in range(int(denominator / 2)):
            value = (total / denominator) * (2 * j + 1) + 1
            mappingx[x] = int(value)
            x += 1
    
    return mappingx


def decodingScramble(local_path):

    """
    This function decodes scramble information from '0.json' to generate a 
    mapping for the images. It uses AES encryption for decoding.
    
    Args:
        local_path (str): The local path to the directory containing the JSON file.

    Returns:
        dict or False: A mapping dictionary for the images or False if 'scramble' is not found in '0.json'.
    """

    logging.debug(f'Decoding scramble')

    # Initialize a mapping dictionary
    mapping_scramble = {}
    
    x = 1
    jumper = 4
    
    # Get the path of the '0.json' file
    zero_json_path = os.path.join(local_path, "0.json")
    
    # Open the '0.json' file
    f = open(zero_json_path)
    
    # Load the JSON data from the file
    images_list = json.load(f)
    
    try:
        # Try to extract the 'scramble' value from the JSON data
        scramble = images_list['scramble']
        scrumble = scramble
    except:
        logging.debug(f'Scramble not found in 0.json')
        # Handle the case where 'scramble' is not found in '0.json'
        # Return False to indicate failure
        return False

    # Initialize an AES cipher for decryption
    aes = AES.new('2606198511121984'.encode("utf8"), AES.MODE_CBC, '2606198511121984'.encode("utf8"))
    
    # Decrypt the 'scramble' value and decode it to UTF-8
    decoded_array = aes.decrypt(base64.b64decode(scramble))
    decoded_array = decoded_array.decode("utf-8")
    
    # Remove any carriage returns from the decoded data
    decoded_array = decoded_array.replace('\r', '')
    
    # Parse the decoded data into a list
    decoded_array_list = json.loads(decoded_array)

    # Extract mappings from the decoded data
    for i in decoded_array_list[0]:
        mapping_scramble[x] = i + 1
        x += 1

    for i in decoded_array_list[1:]:
        for value in i:
            mapping_scramble[x] = value + jumper + 1
            x += 1
        jumper *= 2
    
    return mapping_scramble


def extract_images(local_path, mappingx, num_json):

    """
    This function extracts images from JSON files based on the 
    provided mapping and JSON file numbers. It returns a 
    dictionary of images.

    Args:
        local_path (str): The local path to the directory containing the JSON files.
        mappingx (dict): A mapping dictionary used for processing JSON files.
        num_json (int): The number of JSON files available.

    Returns:
        dict: A dictionary of images.

    """

    logging.debug(f'Extracting Images')

    # Initialize image counter and image dictionary
    image_name = 1
    image_dictx = {}

    # Loop through JSON file numbers (1 to 9)
    for json_file_number in range(1, 10):
        # Get the path for the current JSON file
        path = os.path.join(local_path, str(json_file_number) + ".json")

        try:
            # Open and load the JSON file
            f = open(path)
            images_list = json.load(f)
            
            # # Loop through the images in the JSON file
            # for image_b64 in images_list:
            #     # Decode base64 image and add it to the image dictionary
            #     image_dictx[mappingx[image_name]] = cv2.imdecode(
            #         np.frombuffer(base64.b64decode(image_b64), dtype=np.uint8), flags=1)
            
            # # Loop through the images in the JSON file
            for image_b64 in images_list:
                image_bgr = cv2.imdecode(
                    np.frombuffer(base64.b64decode(image_b64), dtype=np.uint8), flags=1)
                image_rgb=cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
                image_dictx[mappingx[image_name]] = image_rgb
                image_name += 1
                
        except:
            print("")
            # Handle the case where the JSON file is not present
            
    return image_dictx


def mp4Writer(id_num, num_json, image_dict):

    """
    This function generates a video from the provided image dictionary. 
    It uses the ImageSequenceClip class from the MoviePy library to 
    create the video. The resulting video is saved locally, 
    uploaded to GCP, and has music added.

    Args:
        id_num (str): A unique identifier for the video.
        num_json (int): The number of JSON files available.
        image_dict (dict): A dictionary of images.

    Returns:
        None

    """

    logging.debug(f'Writing MP4 for id_num: {id_num}')

    # Get dimensions of the first image in the dictionary
    height, width, layers = image_dict[1].shape
    
    # Set the size of the video
    size = (width, height)
    
    # Get the current file path
    path = os.path.dirname(os.path.realpath(__file__))
    
    # Create a list of images from the image dictionary
    image_list = [image_dict[i] for i in range(1, pow(2, num_json) + 1)]
    
    # Create a video clip from the list of images
    out = ImageSequenceClip(image_list, fps=config.fps)
    
    # Write the video file with the specified codec
    out.write_videofile(os.path.join(os.path.join(path, id_num), config.video_filename), codec='libx264')
    
    # Upload the video file to GCP
    upload_to_gcp(os.path.join(os.path.join(path, id_num), config.video_filename), id_num)
    
    # Add music to the video
    add_music_to_video(os.path.join(os.path.join(path, id_num), config.video_filename), id_num)


def add_music_to_video(video_path, id_num):

    """
    This function adds background music to a video. It selects a 
    random music file from the 'Music' folder, combines it 
    with the video, and saves the resulting video with music.
    
    Args:
        video_path (str): The local path to the video file.
        id_num (str): A unique identifier for the video.

    Returns:
        None

    """

    logging.debug(f'Adding music to video for id_num: {id_num}')

    # Load the video clip from the specified path
    video = VideoFileClip(video_path)
    
    # Get video duration to trim the music according to the length of video    
    video_duration = video.duration

    # Get the folder path where the script is located
    folder_path = os.path.dirname(os.path.realpath(__file__))
    
    # Define the folder containing music files
    music_folder = config.music_folder_path
    
    # List all files in the music folder
    music_files = os.listdir(music_folder)
    
    # Choose a random music file
    selected_music = random.choice(music_files)
    
    # Load the selected music as an audio clip
    music = AudioFileClip(os.path.join(music_folder, selected_music)).subclip(0, video_duration)

    # Set the audio of the video clip as the background music
    video = video.set_audio(music)

    # Write the final video with the added background music
    video.write_videofile(os.path.join(os.path.join(folder_path, id_num), config.video_with_music_filename), codec='libx264', audio_codec='aac')

    # Close the video and music clips
    video.close()
    music.close()
    
    # Upload the video with music to GCP
    upload_to_gcp1(os.path.join(os.path.join(folder_path, id_num), config.video_with_music_filename), id_num)



def upload_to_gcp(path, id_num):

    """
    This function uploads a video file to Google Cloud Storage. It uses 
    the provided path parameter to locate the video file on the local system.
    
    Args:
        path (str): The local path to the video file.
        id_num (str): A unique identifier for the video.

    Returns:
        None

    """

    logging.debug(f'Uploading original video to GCP for id_num: {id_num}')

    # Retrieve the Google Cloud Platform (GCP) key from the configuration
    key = config.gcp_key 
    
    # Create GCP credentials from the service account key
    credential = service_account.Credentials.from_service_account_info(key)
    
    # Create a client to interact with GCP storage
    client = dns.Client(credentials=credential)
    
    # Get the bucket named 'd360us'
    bucket = client.get_bucket(config.gcp_bucket)
    
    # Define the destination path within the bucket
    destination_path = config.gcp_path + str(id_num) + "/" + config.video_filename
    
    # Get a blob (file) within the bucket
    blob = bucket.blob(destination_path)
    
    # Upload the file from the specified local path to GCP storage
    blob.upload_from_filename(path)


def upload_to_gcp1(path, id_num):

    """
    This function uploads a video with music file to Google Cloud Storage. 
    Similar to the previous function, it uses the provided path parameter 
    to locate the file on the local system.

    Args:
        path (str): The local path to the video file with music.
        id_num (str): A unique identifier for the video.

    Returns:
        None

    """

    logging.debug(f'Uploading original video with to GCP for id_num: {id_num}')

    # Retrieve the Google Cloud Platform (GCP) key from the configuration
    key = config.gcp_key 
    
    # Create GCP credentials from the service account key
    credential = service_account.Credentials.from_service_account_info(key)
    
    # Create a client to interact with GCP storage
    client = dns.Client(credentials=credential)
    
    # Get the bucket named 'd360us'
    bucket = client.get_bucket(config.gcp_bucket)
    
    # Define the destination path within the bucket
    destination_path = config.gcp_path + str(id_num) + "/" + config.video_with_music_filename
    # Get a blob (file) within the bucket
    blob = bucket.blob(destination_path)
    
    # Upload the file from the specified local path to GCP storage
    blob.upload_from_filename(path)
