# Twosense Events Collector

This is a simple script that collects events from the Twosense API and stores them in `.json` file.
The next time it runs, it will only collect new events.
## Setup
```bash
    pip install -r requirements.txt
```

## Run
[Get an API access token](https://twosense.readme.io/reference/authentication#2-obtain-an-access-token).
```bash
    export TWOSENSE_API_TOKEN=<TOKEN>
    python collect_events.py
```