import json
import os

import requests

# Twosense API access token. Get it here:
# https://twosense.readme.io/reference/authentication#2-obtain-an-access-token
API_TOKEN = os.getenv("TWOSENSE_API_TOKEN")
API_URL = "https://webapi.twosense.ai/events"
LOG_FILE = "events.json"


def fetch_events(since: str | None) -> list[dict]:
    """
    Fetch events from the Twosense API.

    :param since: Only fetch events that occurred after this time.
    :return: List of events.
    """
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    params = {"since": since} if since else {}

    response = requests.get(API_URL, headers=headers, params=params)
    response.raise_for_status()

    events = response.json()["events"]

    while response.links.get("next"):
        response = requests.get(response.links["next"]["url"], headers=headers)
        response.raise_for_status()

        events += response.json()["events"]

    return events


def save_events(events: list[dict]) -> None:
    """
    Save events to a JSON file. Append to existing events if the file exists.

    :param events: List of events.
    """
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        old_events = json.load(file)

    events = old_events + events

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(events, file, indent=2)


def get_last_event_time(filename: str) -> str | None:
    """
    Get the time of the last event downloaded from the log file.

    :param filename: Path to the log file.
    :return: Time of the last event, or None if the file does not exist.
    """
    if not os.path.exists(filename):
        return None

    with open(filename, "r", encoding="utf-8") as file:
        events = json.load(file)
        return events[-1].get("published")


def main():
    last_event_time = get_last_event_time(LOG_FILE)

    events = fetch_events(last_event_time)
    print(f"Found {len(events)} new events")

    if events:
        save_events(events)
        print(f"Events saved to {LOG_FILE}")


if __name__ == "__main__":
    main()
