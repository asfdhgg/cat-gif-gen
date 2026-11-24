import argparse
import os
import sys
import time
import requests

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

GIPHY_API_KEY = os.getenv("GIPHY_API_KEY", "")

def fetch_from_cataas():
    resp = requests.get("https://cataas.com/cat/gif?json=true", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    gif_id = data.get("_id") or data.get("id", "")
    return f"https://cataas.com/cat/{gif_id}" if gif_id else "https://cataas.com/cat/gif"


def fetch_from_giphy():
    params = {"api_key": GIPHY_API_KEY, "tag": "cat", "rating": "g"}
    resp = requests.get("https://api.giphy.com/v1/gifs/random", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()["data"]["images"]["original"]["url"]


def fetch_from_thecatapi():
    params = {"mime_types": "gif", "limit": 1}
    resp = requests.get("https://api.thecatapi.com/v1/images/search", params=params, timeout=10)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError("No results from TheCatAPI")
    return results[0]["url"]


SOURCES = {
    "cataas": fetch_from_cataas,
    "giphy": fetch_from_giphy,
    "thecatapi": fetch_from_thecatapi,
}


def post_to_discord(gif_url):
    if DISCORD_WEBHOOK_URL == "YOUR_WEBHOOK_URL_HERE":
        sys.exit(1)

    print(f"  Downloading {gif_url} ...")
    r = requests.get(gif_url, timeout=20)
    r.raise_for_status()

    resp = requests.post(
        DISCORD_WEBHOOK_URL,
        files={"file": ("cat.gif", r.content, "image/gif")},
        timeout=30,
    )

    if resp.status_code in (200, 204):
        print("Sent!")
    else:
        print(f"Discord error {resp.status_code}: {resp.text}")


def main():
    parser = argparse.ArgumentParser(description="Post cat GIFs to Discord forever")
    parser.add_argument("--interval", type=float, default=30,
                        help="Seconds between posts (default: 30)")
    parser.add_argument("--source", choices=list(SOURCES.keys()), default="cataas",
                        help="GIF source (default: cataas)")
    args = parser.parse_args()

    fetch_fn = SOURCES[args.source]

    count = 0
    while True:
        count += 1
        print(f"[#{count}] cat gifs")
        try:
            url = fetch_fn()
            post_to_discord(url)
        except KeyboardInterrupt:
            print("bye!")
            sys.exit(0)
        except Exception as e:

        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
