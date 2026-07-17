import psycopg2

import os
from dotenv import load_dotenv

import pycountry

#loads env file
load_dotenv()

try:
    #stores env values into variables
    databaseName = os.getenv("PGDATABASE")
    databaseUsername = os.getenv("PGUSER")
    databasePassword = os.getenv("PGPASSWORD")
    databaseHost = os.getenv("PGHOST")


    #connect to the database   
    connection = psycopg2.connect(
        dbname=databaseName,
        user=databaseUsername,
        password=databasePassword,
        host=databaseHost
    )

    #create cursor to perform database operations
    cur = connection.cursor()


    #populate database
    for country in pycountry.countries:
        cur.execute("INSERT INTO countries (name, iso2, iso3) values (%s, %s, %s) ON CONFLICT DO NOTHING", 
                    (country.name, country.alpha_2, country.alpha_3))
        
    connection.commit()

    
except psycopg2.errors.ProgrammingError as e:
    print("syntax errors, missing columns, or calling a function with the wrong number of arguments")
    print(f"Programming error: {e}")
except psycopg2.errors.OperationalError as e:
    print("Connection drops, times out, or the server shuts down mid-execution.")
    print(f"Programming error: {e}")
except psycopg2.errors.IntegrityError as e:
    print("FOREIGN KEY fails or a NOT NULL constraint is violated")
    print(f"Programming error: {e}")
except Exception as e:
    print("Database Error")
    print(f"Programming error: {e}")
finally:
    #close connection to the database
    print("Closing Connection")
    if 'cur' in locals(): 
        cur.close()
    if 'connection' in locals(): 
        connection.close()
    