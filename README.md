[![Moneylover reporter](https://github.com/svillegasz/money-lover-reporter/actions/workflows/cron.yml/badge.svg)](https://github.com/svillegasz/money-lover-reporter/actions/workflows/cron.yml)

# google-api-selenium-auth

## Requirements
- [Python 3.9 installed](https://www.python.org/downloads/release/python-390/)
- [Poetry installed](https://python-poetry.org/docs/)
- Active [serpsbot](https://serpsbot.com/) account

## Environment Variables

To run this project, you will need to define the following environment variables

`GOOGLE_USER` for the google account with your notifications emails

`GOOGLE_PASSWORD` for the google account with your notifications emails

`MONEY_LOVER_USER`

`MONEY_LOVER_PASSWORD`

`SERPSBOT_API_KEY` from serpsbot account


## Installation

Install dependencies using poetry

```bash
  poetry install
```

## Usage
Run reporter using poetry

```bash
poetry run python main.py
```


## Customization
```
main.py
```
Depending on your financial services (e.g. credit card, savings account), you will need to add/update:
1. Service emails constants: what emails are used from your financial service to send you notifications, e.g.
```python
BANCOLOMBIA_EMAIL = 'alertasynotificaciones@notificacionesbancolombia.com'
```
2. For each service email you need to add a method `process_{service_name}_message(message)` and `update_{service_name}_wallet(messages)`
