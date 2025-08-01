# Premier League Data Pipeline

This project contains a set of Python scripts to fetch football data from the api-football.com API and load it into a PostgreSQL database hosted in Neondb. It is designed to collect data for the Premier League (League ID 39) for the 2018-2019 and 2021-2022 seasons.

## Features

- Fetches and loads data for:
    - Teams and their coaches for each season.
    - Players and their seasonal stats.
    - Team transfers.
    - Trophies won by players and coaches.
- Uses a `.env` file to manage the API key and database URL securely.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <https://github.com/IanMwai/footbal_dashboard/>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up the Environment Variables:**
    - Create a file named `.env` in the root of the project.
    - Add your API key and Neon database URL to the `.env` file as follows:
      ```
      API_KEY=your_api_key_here
      NEON_DB_URL=your_neon_db_url_here
      ```

4.  **Database Schema:**
    - The `run_all.py` script will automatically create the necessary tables in your database. 
    - If you are running the scripts for the first time, or if your database is empty, running `python run_all.py` is the recommended way to set up the schema.
    - Alternatively, you can manually create the schema by copying the contents of `schema.sql` and executing it in the Neon SQL editor.

## Usage

To run the entire data loading pipeline, execute the `run_all.py` script:

```bash
python run_all.py
```

This will first create the database schema (if the tables don't exist) and then run the individual loading scripts in the correct order.

### Individual Scripts

If you need to run a script individually, you must follow this order to ensure data integrity:

1.  `load_teams_and_coaches.py`
2.  `load_players_and_stats.py`
3.  `load_transfers.py`
4.  `load_trophies.py`

**Note:** Before running any individual script, ensure that the database schema has been created, either by running `run_all.py` at least once or by creating the tables manually.

**P.S.** You might need to upgrade your API-Football plan to make all the required requests.