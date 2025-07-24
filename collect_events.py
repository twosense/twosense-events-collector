import json
import logging
import os
import time

import jwt
import requests

logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] - %(message)s",
    level=logging.INFO,
)

CLIENT_ID = os.getenv("TWOSENSE_API_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWOSENSE_API_CLIENT_SECRET")

API_URL = "https://webapi.twosense.ai/events"
LOG_FILE = "events.json"
STATE_FILE = "state.json"


def main():
    logging.info("Starting event collection")

    state = read_state()
    last_event_time = state.get("last_event_time")
    if last_event_time:
        logging.info(f"Collecting events since {last_event_time}")

    api_token = state.get("api_token")
    if not is_valid(api_token):
        api_token = refresh_api_token()

    # Fetch events from the Twosense API
    events = fetch_events(api_token, last_event_time)
    logging.info(f"Found {len(events)} new events")

    if not events:
        logging.info("No new events found")
        return

    # Save events to a JSON file
    save_events(events)

    # Update the state file
    last_event_time = events[-1]["published"]
    state["last_event_time"] = last_event_time
    state["api_token"] = api_token
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file)
    logging.info(f"State updated with last event time {last_event_time}")

    logging.info("Done")
    logging.info(50 * "=")


def fetch_events(api_token: str, since: str | None) -> list[dict]:
    """
    Fetch events from the Twosense API.

    :param api_token: API access token.
    :param since: Only fetch events that occurred after this time.
    :return: List of events.
    """
    headers = {
        "Authorization": f"Bearer {api_token}",
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

    logging.info(f"Events saved to {LOG_FILE}")


def read_state() -> dict:
    """
    Get the time of the last event downloaded from the log file.

    :return: Time of the last event, or None if the file does not exist.
    """
    if not os.path.exists(STATE_FILE):
        return {}

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def is_valid(api_token: str) -> bool:
    if not api_token:
        logging.warning("No API token found")
        return False

    try:
        now = int(time.time())
        decoded = jwt.decode(api_token, options={"verify_signature": False})
        if decoded["exp"] < now:
            logging.warning("API token has expired")
            return False
    except Exception as e:
        logging.error(f"Error decoding API token: {e}")
        return False

    logging.info(f"API token is valid")
    return True


def refresh_api_token():
    logging.info("Refreshing API token")

    payload = (
        f'{{"client_id":"{CLIENT_ID}",'
        f'"client_secret":"{CLIENT_SECRET}",'
        '"audience":"https://webapi.twosense.ai",'
        '"grant_type":"client_credentials"}'
    )
    headers = {"content-type": "application/json"}

    response = requests.post(
        "https://webapi.twosense.ai/oauth/token", data=payload, headers=headers
    )
    response.raise_for_status()

    return response.json()["access_token"]


if __name__ == "__main__":
    main()
