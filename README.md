# Twosense Events Collector

This is a simple script that collects events from the Twosense API and stores them in `.json` file.
The next time it runs, it will only collect new events.

## Requirements

- Python 3.11+
- A Twosense API client id and client secret

## Setup

```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```

## Run

```bash
    export TWOSENSE_API_CLIENT_ID=<you_client_id>
    export TWOSENSE_API_CLIENT_SECRET=<you_client_secret>
    
    python collect_events.py
```