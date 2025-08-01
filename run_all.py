#Importing the function to get a database connection.
from utils.db import get_db_connection

def create_schema():
    """Creates the database schema by executing the schema.sql file."""
    print("Creating database schema...")
    try:
        with open('schema.sql', 'r') as f:
            sql = f.read()
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                conn.commit()
        print("Schema created successfully.")
    except Exception as e:
        print(f"An error occurred during schema creation: {e}")
        exit(1)

if __name__ == "__main__":
    #Create the database schema before running the data loaders.
    create_schema()

    #Import the data loading scripts to execute them.
    print("Starting data loading scripts...")
    import load_teams_and_coaches
    import load_players_and_stats
    import load_transfers
    import load_trophies

    print("\nAll scripts completed successfully!")
