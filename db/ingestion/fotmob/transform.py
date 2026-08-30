def extract_teams(data, country_id):

    # handles edge cases such as
    # if the league has conferences, and if the league was established then
    if not data.get("table"):
        return []
    league_data = data["table"][0]["data"]

    if league_data.get("composite"):
        items = league_data["tables"][2]["table"]["all"]
    else:
        items = league_data["table"]["all"]

    # dictionary
    teams = []

    for team in items:
        team = {
            "fotmob_id": team["id"],
            "name": team["name"],
            "short_name": team["shortName"],
            "country_id": country_id,
        }

        teams.append(team)

    return teams


def extract_player_minutes(data, fotmob_season_id):

    player_data = data["props"]["pageProps"]["data"]["statsData"]

    players = []

    for player in player_data:
        player = {
            "fotmob_id": player["id"],
            "name": player["name"],
            "team_fotmob_id": player["teamId"],
            "position": player["position"],
            "mins_played": player["statValue"]["value"],
            "fotmob_season_id": fotmob_season_id,
        }

        players.append(player)

    return players
