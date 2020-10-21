import logging
import os
import pandas
import pymongo
import typing

from . import commons
from . import db

logger = logging.getLogger()


def load_csv_table(table, url=None):
    """ Populate the database from a csv file. Initial migration. """
    if not os.path.isfile(table):
        raise ValueError(f'Failed to load csv data. File "{table}" does not exist')

    df: typing.Optional[pandas.DataFrame] = pandas.read_csv(table)

    dbm = db.DBManager()
    groups = {}

    # parse other columns
    for index, row in df.iterrows():
        group_name = row["group"]
        if group_name not in groups:
            groups[group_name] = commons.Group(name=group_name, enabled=True)
            dbm.create_group(groups[group_name])
            logger.info(f"Creating group {groups[group_name]}")

        entry = commons.Entry(
            sms_queue=None,
            group=groups[group_name],
            **{
                "pvname": row["PV"],
                "emails": row["emails"],
                "condition": row["condition"].lower().strip(),
                "alarm_values": row["specified value"],
                "unit": row["measurement unit"],
                "warning_message": row["warning message"],
                "subject": row["email subject"],
                "email_timeout": row["timeout"],
            },
        )
        try:
            dbm.create_entry(entry)
            logger.info(f"Creating entry {entry}")
        except pymongo.errors.DuplicateKeyError:
            logger.warn(f"Entry exists {entry}")
        except commons.EntryException:
            logger.exception("Failed to create entry")

        dbm.disconnect()
