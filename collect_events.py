import json
import os

import requests

# Twosense API access token. Get it here:
# https://twosense.readme.io/reference/authentication#2-obtain-an-access-token
API_TOKEN = os.getenv("TWOSENSE_API_TOKEN")
API_URL = "https://webapi.twosense.ai/events"
LOG_FILE = "events.json"


def fetch_events(last_event_time: str | None):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    params = {"since": last_event_time} if last_event_time else {}

    response = requests.get(API_URL, headers=headers, params=params)
    response.raise_for_status()

    events = response.json()["events"]

    while response.links.get("next"):
        response = requests.get(response.links["next"]["url"], headers=headers)
        response.raise_for_status()

        events += response.json()["events"]

    return events


def save_events(events: list[dict]):
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as file:
            json.dump([], file)

    with open(LOG_FILE, "r") as file:
        old_events = json.load(file)

    events = old_events + events

    with open(LOG_FILE, "w") as file:
        json.dump(events, file, indent=2)


def get_last_event_time(filename: str) -> str | None:
    try:
        with open(filename, "r") as file:
            events = json.load(file)
            return events[-1]["published"]
    except (FileNotFoundError, IndexError):
        return None


def main():
    last_event_time = get_last_event_time(LOG_FILE)

    events = fetch_events(last_event_time)
    print(f"Found {len(events)} new events")

    if events:
        save_events(events)
        print(f"Events saved to {LOG_FILE}")


if __name__ == "__main__":
    main()
