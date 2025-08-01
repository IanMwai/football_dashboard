import os
from dotenv import load_dotenv

#Load environment variables from .env file.
load_dotenv()

#Get API key from environment variables.
API_KEY = os.getenv("API_KEY")

#Raise an error if the API key is not found.
if not API_KEY:
    raise ValueError("API_KEY not found. Please add it to your .env file.")

#Define the headers for the API requests.
HEADERS = {
    "x-apisports-key": API_KEY
}