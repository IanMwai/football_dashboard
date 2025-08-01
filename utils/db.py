import psycopg2
import os
from dotenv import load_dotenv

#Load environment variables from .env file.
load_dotenv()

#Defining a function to get a database connection.
def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    #Get the database connection URL from the environment variables.
    db_url = os.getenv("NEON_DB_URL")
    
    #Raise an error if the database connection URL is not found.
    if not db_url:
        raise ValueError("NEON_DB_URL not found. Please add it to your .env file.")
    
    #Connect to the database and return the connection object.
    return psycopg2.connect(db_url)