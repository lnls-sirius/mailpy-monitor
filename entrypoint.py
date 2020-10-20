#!/usr/bin/env python3
import logging
import logging.config
import argparse
import yaml
import typing
import multiprocessing

import app
import app.sms
import app.ioc
import app.commons

if __name__ == "__main__":
    with open("app/logging.yaml", "r") as f:
        log_config = yaml.safe_load(f)

    logging.config.dictConfig(log_config)

    parser = argparse.ArgumentParser(
        description="Monitor PV EPICS values and if any of them isn't in a specified range, "
        "email a warning message to a list of targets."
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
        "-t",
        "--table",
        metavar="my_table.csv",
        default="sms_table.csv",
        help="choose the csv file to read data from (default: sms_table.csv)",
    )
    args = parser.parse_args()

    # SMS
    sms_app = app.sms.SMSApp(
        tls=args.tls,
        login=args.login,
        passwd=args.passwd,
        table=args.table,
        sms_queue=app.SMS_QUEUE,
        ioc_queue=app.IOC_QUEUE,
    )

    sms_app.load_csv_table()
    sms_app.start()

    groups: typing.Dict[str, int] = {}
    for k, v in sms_app.groups.items():
        groups[k] = v.enabled

    ioc_process = multiprocessing.Process(
        name="IOCProcess",
        target=app.ioc.start_ioc,
        kwargs={
            "groups": groups,
            "sms_queue": app.SMS_QUEUE,
            "ioc_queue": app.IOC_QUEUE,
        },
        daemon=False,
    )

    ioc_process.start()
    ioc_process.join()
