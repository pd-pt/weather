
# INSTALLATION

## Install python deps:

`. ./venv/bin/activate`

`pip install -r requirements.txt`

## Run postgres on `localhost:5432` or use docker compose: 

`docker compose up -d database`

## Run django server and telegram bot:

`./run.sh`

## Or use only docker compose to run the project: 

`docker compose up`

# Running tests

`. ./venv/bin/activate`

`pytest`

# TG bot

https://t.me/weather_test23_bot