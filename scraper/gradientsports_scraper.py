"""
Scraper for fc.gradientsports.com player metrics.

The site is built on React Router v7 (Remix) using "single fetch" loaders.
Each route's data is served at <route-path>.data, but the payload isn't
plain JSON -- it's a flattened, reference-deduplicated array. Every value
lives at a numeric index; objects reference other indices via keys shaped
like "_<index>": <value_index>, meaning "the property named arr[index]
has the value at arr[value_index]". Plain JSON arrays of integers are
lists of further indices to resolve. Negative numbers are sentinels for
null/undefined.

This script fetches that raw array and decodes it back into normal
nested JSON, then pulls out the player's grouped stat metrics.

Usage:
    python gradientsports_scraper.py 99000
    python gradientsports_scraper.py 99000 333594 32438   # multiple players
"""

import sys
import json
import time
import urllib.request

BASE_URL = "https://fc.gradientsports.com/rankings/player/{player_id}/metrics.data"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research-scraper/1.0)",
    "Accept": "*/*",
}


def fetch_raw(player_id: int) -> list:
    """Fetch the raw flattened-array payload for a given player id."""
    url = BASE_URL.format(player_id=player_id)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def decode(arr: list):
    """
    Resolve the flattened reference-array format into normal nested
    Python objects. Returns the fully resolved value at index 0 (the
    root node), which is a dict keyed by route id, e.g.
    decoded["routes/rankings/player/metrics"]["data"]["data"]
    """
    cache = {}

    def resolve(i):
        if not isinstance(i, int):
            return i
        if i < 0:
            return None  # sentinel for null/undefined
        if i in cache:
            return cache[i]
        node = arr[i]
        if isinstance(node, dict) and node and all(k.startswith("_") for k in node):
            result = {}
            cache[i] = result
            for k, v in node.items():
                name = arr[int(k[1:])]
                result[name] = resolve(v)
            return result
        elif isinstance(node, list):
            result = []
            cache[i] = result
            for v in node:
                result.append(resolve(v) if isinstance(v, int) else v)
            return result
        else:
            cache[i] = node
            return node

    return resolve(0)


def get_player_metrics(player_id: int) -> dict:
    """Fetch and decode a single player's metrics into a clean dict."""
    raw = fetch_raw(player_id)
    decoded = decode(raw)

    metrics_route = decoded.get("routes/rankings/player/metrics", {})
    data = metrics_route.get("data", {}).get("data", {})

    player_layout = decoded.get("routes/rankings/player/playerProfileLayout", {})
    player_info = player_layout.get("data", {}).get("player", {})

    clean = {
        "id": player_info.get("id", player_id),
        "name": player_info.get("name"),
        "team": (player_info.get("team") or {}).get("name"),
        "position": player_info.get("position"),
        "selectedSeason": data.get("selectedSeason"),
        "selectedLeague": data.get("selectedLeague"),
        "groups": [
            {"groupName": g.get("groupName"), "metrics": g.get("metrics", [])}
            for g in data.get("groupedMetrics", [])
        ],
    }
    return clean


def main():
    if len(sys.argv) < 2:
        print("Usage: python gradientsports_scraper.py <player_id> [more_ids...]")
        sys.exit(1)

    player_ids = sys.argv[1:]
    results = []

    for pid in player_ids:
        print(f"Fetching player {pid}...", file=sys.stderr)
        try:
            results.append(get_player_metrics(int(pid)))
        except Exception as e:
            print(f"  failed for {pid}: {e}", file=sys.stderr)
        time.sleep(1)  # be polite, don't hammer the server

    output = results[0] if len(results) == 1 else results
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
