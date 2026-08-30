from .. import db
from . import client, transform, load
from playwright.sync_api import sync_playwright


def run():

    populate_players()


def populate_players():
    with sync_playwright() as p:
        browser = p.chromium.launch()

        connection = db.connect()
        cur = connection.cursor()

        cur.execute("""SELECT c.country_id, c.fotmob_league_id, c.fotmob_slug, c.season_format, cs.fotmob_season_id
            FROM competitions c
            JOIN competition_seasons cs ON c.id = cs.competition_id
            WHERE c.country_id IS NOT NULL
            AND cs.season_id != 1""")

        leagues = cur.fetchall()

        for league_season in leagues:
            fotmob_ID = league_season[1]
            fotmob_season_id = league_season[4]

            print(f"Fetching players for league {fotmob_ID} season {fotmob_season_id}")

            player_data = client.fetch_player_minutes(
                browser, fotmob_ID, fotmob_season_id
            )
            players = transform.extract_player_minutes(player_data, fotmob_season_id)
            load.load_player(players, fotmob_season_id)

        cur.close()
        connection.close()

        browser.close()


def populate_teams():

    # connect to db and get cursor
    connection = db.connect()
    cur = connection.cursor()

    # retrieve all seasons and competitions
    cur.execute(
        "SELECT country_id, fotmob_league_ID, fotmob_slug, season_format FROM competitions WHERE country_id IS NOT NULL"
    )
    competitionCountryID = cur.fetchall()

    cur.execute("SELECT name FROM seasons")
    tSeasons = cur.fetchall()

    seasons = []

    for season in tSeasons:
        strSeason = season[0]

        firstYear = strSeason[0:4]
        lastYear = strSeason[5:7]
        years = firstYear + "-20" + lastYear

        seasons.append(years)

    for league in competitionCountryID:
        fotmob_ID = league[1]
        fotmobSlug = league[2]
        countryID = league[0]

        for season in seasons:
            if league[3] == "calendar":
                season = season[0:4]

            data = client.fetch_league(fotmob_ID, fotmobSlug, season)
            print(f"Keys for {fotmobSlug} {season}: {list(data.keys())}")
            teams = transform.extract_teams(data, countryID)
            load.load_teams(teams)

    cur.close()
    connection.close()


if __name__ == "__main__":
    run()
