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


def load_player(players, fotmob_season_id):

    connection = db.connect()
    cur = connection.cursor()

    for player in players:
        cur.execute(
            """
            INSERT INTO players (fotmob_id, full_name, primary_position)
            VALUES (%s, %s, %s )
            ON CONFLICT (fotmob_id) DO UPDATE SET 
                primary_position = EXCLUDED.primary_position,
                full_name = EXCLUDED.full_name,
                updated_at = NOW()
            RETURNING id
        """,
            (player["fotmob_id"], player["name"], player["position"]),
        )

        player_id = cur.fetchone()[0]

        cur.execute(
            """
            SELECT id FROM teams WHERE fotmob_id = (%s)
         """,
            (player["team_fotmob_id"],),
        )

        team_id = cur.fetchone()[0]

        cur.execute(
            """
            SELECT season_id FROM competition_seasons WHERE fotmob_season_id = (%s)
        """,
            (fotmob_season_id,),
        )

        season_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO player_seasons (player_id, team_id, season_id, position)
            VALUES (%s, %s, %s, %s) ON CONFLICT (player_id, team_id, season_id) DO UPDATE SET
                position = EXCLUDED.position
        """,
            (player_id, team_id, season_id, player["position"]),
        )

    connection.commit()

    cur.close()
    connection.close()


# if __name__ == "__main__":
#  data = client.fetch_player_minutes(47, 20720)
#  players = transform.extract_player_minutes(data, 20720)
# load_player(players, 20720)
# print("Done")
