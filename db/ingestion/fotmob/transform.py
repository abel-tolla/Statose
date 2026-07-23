def extract_teams(data, country_id):

    # extracting from data
    items = data["table"][0]["data"]["table"]["all"]

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
