# Mailpy

[![codecov](https://codecov.io/gh/carneirofc/mailpy-monitor/branch/master/graph/badge.svg?token=DRM1BMIO9G)](https://codecov.io/gh/carneirofc/mailpy-monitor)

[![Test and Coverage](https://github.com/carneirofc/mailpy-monitor/actions/workflows/tests.yml/badge.svg)](https://github.com/carneirofc/mailpy-monitor/actions/workflows/tests.yml)

[![Lint](https://github.com/carneirofc/mailpy-monitor/actions/workflows/lint.yml/badge.svg)](https://github.com/carneirofc/mailpy-monitor/actions/workflows/lint.yml)

Python app that monitors EPICS PVs, check their specified operation values and perform actions accordingly.

## Usage
Clone the repository and install the sources using pip:
```command
pip install . -v
```

The command `mailpy` will start the alarm server, `mailpy --help` for further instructions.

The utility command `mailpy-db` is available for testing purposes, it will setup a MongoDB container with dummy data.

## Development

Before modifying the source code make sure that `pre-commit` is installed and active.

```bash
pip install -U pre-commit --user
pre-commit install
```

Install the package using the interactive mode:
```bash
pip install -e .
```
**IMPORTANT** Check the directory `scripts-dev` for usefull commands!

Stating a development **mongodb** server:
```python
import mailpy.utils

manager = mailpy.utils.MongoContainerManager()
manager.start()
```
This will start a **mongodb** container with the following settings:
```python
name: str = "MONGODB_TEST_CONTAINER"
port: int = 27017
host: str = "localhost"
database: str = "mailpy"
root_username: str = "admin"
root_password: str = "admin"
username: str = "test"
password: str = "test"
image: str = "mongo:4.4.3-bionic"
```
Use the connection string `mongodb://test:test@localhost:27017/mailpy`.

The application can be started using the following script:

```python
import mailpy_run
mailpy_run.start_alarm_server()
```

### Building Docker Containers
The following scripts are used to build Docker images:

```bash
# Alarm server image
scripts-dev/build.sh

# Build mongodb image, with collection and user setup
scripts-dev/build-db.sh
```

### Tests & Coverage
```
coverage run -m unittest discover && coverage xml && coverage report
```

One can start the mailpy container using on the terminal using the following command:
```bash
docker run \
    --interactive \
    --tty \
    -e MONGODB_URI="mongodb://test:test@localhost:27017/mailpy" \
    -e ALERT_MAIL_PASSWORD="ASD" \
    -e ALERT_MAIL_LOGIN="ASD"  \
    docker.io/carneirofc/mailpy-mail:latest bash
```
This assumes that a valid **mongodb** instance is already running.

## Deploy

Environment varibles:

| ENV         | Desc                                                                                |
| ----------- | ----------------------------------------------------------------------------------- |
| MONGODB_URI | mongodb://\<login>:\<password>@\<host>:\<port>/\<db name> MongoDB connection string |

Secrets or Environment Variables:

| Name                | Desc                             |
| ------------------- | -------------------------------- |
| ALERT_MAIL_PASSWORD | Email password                   |
| ALERT_MAIL_LOGIN    | Email used to send notifications |

## @todo

    - Signal SMS application to update the entries (Create/Update/Remove)
    - Support condition 'decreasing step' (similar to 'increasing step')
    - Consider creating an "user" collection (MongoDB)