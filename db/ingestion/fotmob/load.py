from .. import db


def load_teams(teams):
    # connect to database
    connection = db.connect()
    cur = connection.cursor()

    for team in teams:
        cur.execute(
            """
            INSERT INTO teams (fotmob_id, name, short_name, country_id) 
            VALUES (%s, %s, %s, %s) 
            ON CONFLICT (fotmob_id) DO UPDATE SET
            name = EXCLUDED.name,
            short_name = EXCLUDED.short_name,
            updated_at = NOW()
        """,
            (team["fotmob_id"], team["name"], team["short_name"], team["country_id"]),
        )

    connection.commit()

    cur.close()
    connection.close()
