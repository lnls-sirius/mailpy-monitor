# Mailpy


[![codecov](https://codecov.io/gh/carneirofc/mailpy-monitor/branch/master/graph/badge.svg?token=DRM1BMIO9G)](https://codecov.io/gh/carneirofc/mailpy-monitor)

[![Test and Coverage](https://github.com/carneirofc/mailpy-monitor/actions/workflows/tests.yml/badge.svg)](https://github.com/carneirofc/mailpy-monitor/actions/workflows/tests.yml)

[![Lint](https://github.com/carneirofc/mailpy-monitor/actions/workflows/lint.yml/badge.svg)](https://github.com/carneirofc/mailpy-monitor/actions/workflows/lint.yml)

Python app that monitors EPICS PVs, check their specified operation values and notify via e-mail.


## Build
The followwing scripts are used to build Docker images:
```
scripts-dev/build-db.sh  scripts-dev/build.sh
```

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

| ENV         | Default                                              | Desc                      |
| ----------- | ---------------------------------------------------- | ------------------------- |
| MONGODB_URI | mongodb://<login>:<password>@<host>:<port>/<db name> | MongoDB connection string |

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
