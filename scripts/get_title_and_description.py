# Import necessary modules
import config  # Custom configuration module
from google.oauth2 import service_account  # Google OAuth2 authentication
from google.cloud import storage as dns  # Google Cloud Storage client
import json  # JSON manipulation
import openai  # OpenAI API for text generation
import os  # Operating System functions

def get(ids):
    """
    Generates a title and description for a video based on diamond properties.

    Args:
        ids (str): The ID for the diamond.

    Returns:
        title (str): Generated title for the video.
        description (str): Generated description for the video.
    """

    # Get GCP key from configuration
    key = config.gcp_key

    # Create a GCP credentials object
    credential = service_account.Credentials.from_service_account_info(key)

    # Create a GCP storage client
    client = dns.Client(credentials=credential)

    # Get the GCP bucket
    bucket = client.get_bucket(config.gcp_bucket)    
    blob = bucket.blob(config.gcp_path + ids + "/.json")
    file_content = blob.download_as_text()

    # Parse the JSON content
    json_data = json.loads(file_content)['PROPERTIES']

    # Set up OpenAI API key
    openai.api_key = config.openai_api_key

    # Generate title
    context_title = config.title_prompt
    response_title = openai.Completion.create(
        engine= config.openai_engine,
        prompt=context_title + str(json_data),
        max_tokens=config.openai_max_tokens,
        temperature= config.openai_temperature
    )
    title = response_title.choices[0].text.strip()

    # Generate description
    context_desc = config.description_prompt   
    
    response_desc = openai.Completion.create(
        engine= config.openai_engine,
        prompt= context_desc + str(json_data),
        max_tokens= config.openai_max_tokens,
        temperature= config.openai_temperature,
    )
    description = response_desc.choices[0].text.strip()

    return title, description
