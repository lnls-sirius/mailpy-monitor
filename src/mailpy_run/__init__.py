#!/usr/bin/env python3
import argparse

import mailpy.logging as logging

logger = logging.getLogger()


def start_test_database():
    import mailpy.utils

    logging.load_config()

    parser = argparse.ArgumentParser(
        description="Start a dummy mongodb with some test data"
    )
    parser.parse_args()
    m = mailpy.utils.MongoContainerManager()
    print(f"Stating mongodb container based on {m.config.image}")
    print(
        f"connection string: 'mongodb://{m.config.username}:{m.config.password}@{m.config.host}:{m.config.port}/{m.config.database}'"
    )
    m.start()


def start_alarm_server():
    import os

    import mailpy.manager

    parser = argparse.ArgumentParser(
        description="Monitor PV EPICS values and if any of them isn't in a specified range, "
        "email a warning message to a list of targets."
    )
    parser.add_argument(
        "--logging-config",
        help="yml config file for logging",
        dest="logging_config",
    )
    parser.add_argument(
        "--tls",
        action="store_true",
        help="start an unsecured SMTP connection and encrypt it using .starttls() (default: use SMTP_SSL)",
    )
    parser.add_argument(
        "--login",
        metavar="email@example.com",
        default="controle.supervisorio@gmail.com",
        help="define the sender email (default: controle.supervisorio@gmail.com)",
    )
    parser.add_argument(
        "-p",
        "--passwd",
        metavar="my_password",
        required=True,
        help="set the password used when trying to log in",
    )
    parser.add_argument(
        "-db",
        "--db_url",
        metavar="mongodb://localhost:27017/mailpy",
        default="mongodb://localhost:27017/mailpy",
        help="MongoDB connection URL",
    )

    args = parser.parse_args()
    logging_config = args.logging_config
    if not logging_config:
        print(
            f"logging_config '{logging_config}' setting is empty, using the default rotating file config"
        )
        logging.load_config_rotating_file()

    # SMS
    sms_app = mailpy.manager.Manager(
        config=mailpy.manager.Config(
            email_tls_enabled=args.tls,
            email_login=args.login,
            email_password=args.passwd,
            db_connection_string=args.db_url,
        )
    )
    sms_app.initialize_entries_from_database()
    sms_app.start()
    sms_app.join()