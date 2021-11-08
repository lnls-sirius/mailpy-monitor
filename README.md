# Mailpy

[![codecov](https://codecov.io/gh/carneirofc/mailpy-monitor/branch/master/graph/badge.svg?token=DRM1BMIO9G)](https://codecov.io/gh/carneirofc/mailpy-monitor)

[![Test and Coverage](https://github.com/carneirofc/mailpy-monitor/actions/workflows/tests.yml/badge.svg)](https://github.com/carneirofc/mailpy-monitor/actions/workflows/tests.yml)

[![Lint](https://github.com/carneirofc/mailpy-monitor/actions/workflows/lint.yml/badge.svg)](https://github.com/carneirofc/mailpy-monitor/actions/workflows/lint.yml)

Python app that monitors EPICS PVs, check their specified operation values and notify via e-mail.

# Usage
Clone the repository and install the sources using pip:
```command
pip install . -v
```

The command `mailpy` will start the alarm server, `mailpy --help` for further instructions.

The utility command `mailpy-db` is available for testing purposes, it will setup a MongoDB container with dummy data.

## Build
The following scripts are used to build Docker images:
```
# Alarm server image
scripts-dev/build.sh

# Build mongodb image, with collection and user setup
scripts-dev/build-db.sh
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

| ENV         | Desc                                                                           |
| ----------- | ------------------------------------------------------------------------------ |
| MONGODB_URI | mongodb://<login>:<password>@<host>:<port>/<db name> MongoDB connection string |

Secrets or Environment Variables:

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
