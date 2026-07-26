from db.ingestion.fotmob import transform

data = {
    "table": [
        {
            "data": {
                "table": {
                    "all": [
                        {"id": 9825, "name": "Arsenal", "shortName": "Arsenal"},
                        {"id": 8456, "name": "Manchester City", "shortName": "Man City"}
                    ]
                }
            }
        }
    ]
}


def test_extract_teams():
    expected_value = [
        {"fotmob_id": 9825, "name": "Arsenal", "short_name": "Arsenal", "country_id": 500},
        {"fotmob_id": 8456, "name": "Manchester City", "short_name": "Man City", "country_id": 500}
    ]
        
    result = transform.extract_teams(data, 500)
    assert result == expected_value