import psycopg2

import os
from dotenv import load_dotenv

load_dotenv()


def connect():
    try:
        databaseName = os.getenv("PGDATABASE")
        databaseUsername = os.getenv("PGUSER")
        databasePassword = os.getenv("PGPASSWORD")
        databaseHost = os.getenv("PGHOST")

        connection = psycopg2.connect(
            dbname=databaseName,
            user=databaseUsername,
            password=databasePassword,
            host=databaseHost,
        )

        return connection

    except Exception as e:
        print("Unable to connect to Database")
        print(f"Error: {e}")
        raise
