# Mailpy


[![codecov](https://codecov.io/gh/carneirofc/mailpy-monitor/branch/master/graph/badge.svg?token=DRM1BMIO9G)](https://codecov.io/gh/carneirofc/mailpy-monitor)

[![Lint](https://github.com/carneirofc/mailpy-monitor/actions/workflows/lint.yml/badge.svg)](https://github.com/carneirofc/mailpy-monitor/actions/workflows/lint.yml)

Python app that monitors PVs EPICS, check their specified operation values and send an e-mail to a list of targets with a warning message if the PV value exceed its limits.

This code reads a list of EPICS PVs and their corresponding specified values
from a MongoDB and monitor them. If any these PVs is not in it's specified
value, an e-mail is sent with a warning message to one or a list of e-mail
address.

## Tests & Coverage
```
coverage run -m unittest discover && coverage xml && coverage report
```

Manual testing deploy

```
docker run --interactive --tty -e MONGODB_URI="mongodb://test:test@localhost:27017/mailpy" -e ALERT_MAIL_PASSWORD="ASD" -e ALERT_MAIL_LOGIN="ASD"  docker.io/carneirofc/mailpy-mail:latest bash
```

## Deploy

Environment varibles:

| ENV         | Default                             | Desc                      |
| ----------- | ----------------------------------- | ------------------------- |
| MONGODB_URI | mongodb://localhost:27017/mailpy-db | MongoDB connection string |

Secrets:

| Name                | Desc                             |
| ------------------- | -------------------------------- |
| ALERT_MAIL_PASSWORD | Email password                   |
| ALERT_MAIL_LOGIN    | Email used to send notifications |

## Development

Install **pre-commit** !

### To do:

    - Signal SMS application to update the entries (Create/Update/Remove)
    - Support condition 'decreasing step' (similar to 'increasing step')
    - Consider creating an "user" collection (MongoDB)
    - Consider removing the IOC, access only via the API

## Usage

### Include new entries

One could use the rest API and the front-end or use `scripts/*.py`.

Start an interactive python session at the project root:

```python
import app.utility

app.utility.connect()

# Create a single entry
app.utility.create_entry(...)

# Create entries from a csv file
app.utility.load_csv_table("sms_table.csv")

# Disconnect
app.utility.disconnect()

```

### Syntax:

    - separate e-mails with semicolon (";")
        e.g.: "unknown.user@mail.com;another_user@aMail.com"
    - separate specified value with colon (":")
        e.g.:

| Conditions      | Description | Syntax                |
| --------------- | ----------- | --------------------- |
| out of range    |             | "17:22"               |
| increasing step |             | "1.0:1.5:2.0:2.5:3.0" |
| superior than   |             | "42"                  |
| inferior than   |             | "46"                  |
