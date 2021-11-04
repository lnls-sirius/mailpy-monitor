import dataclasses
import logging
import typing

import pymongo
import pymongo.database

from app.entities import ConditionEnums

from .connector import DBConnector

logger = logging.getLogger()


# @dataclasses.dataclass
class GroupData(typing.NamedTuple):
    id: str
    name: str
    enabled: bool
    description: str


class EntryData(typing.NamedTuple):
    id: str
    pvname: str
    emails: typing.List[str]
    condition: str
    alarm_values: str
    unit: str
    warning_message: str
    subject: str
    email_timeout: float
    group: str


class DBManager:
    CONDITIONS_COLLECTION = "conditions"
    GROUPS_COLLECTION = "groups"
    ENTRIES_COLLECTION = "entries"

    def __init__(self, connector: DBConnector):
        self._connector: DBConnector = connector

    @property
    def db(self) -> pymongo.database.Database:
        return self._connector.db

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self._connector.close()

    def _parse_group(self, data: typing.Any) -> GroupData:
        return GroupData(
            description=data.get("description", ""),
            enabled=bool(data["enabled"]),
            id=str(data["_id"]),
            name=data["name"],
        )

    def _parse_entry(self, data: typing.Any) -> EntryData:
        return EntryData(
            id=str(data["_id"]),
            pvname=data["pvname"],
            emails=data["emails"].strip().split(":"),
            condition=data["condition"],
            alarm_values=data["alarm_values"],
            unit=data["unit"],
            warning_message=data["warning_message"],
            subject=data["subject"],
            email_timeout=data["email_timeout"],
            group=data["group"],
        )

    def get_entries(self) -> typing.List[EntryData]:
        entries: pymongo.collection.Collection = self.db[DBManager.ENTRIES_COLLECTION]
        return [self._parse_entry(e) for e in entries.find()]

    def get_group(self, group_name: str) -> typing.Optional[GroupData]:
        groups: pymongo.collection.Collection = self.db[DBManager.GROUPS_COLLECTION]
        return self._parse_group(groups.find_one({"name": group_name}))

    def get_condition(self, name: str):
        conditions: pymongo.collection.Collection = self.db[
            DBManager.CONDITIONS_COLLECTION
        ]
        return conditions.find_one({"name": name})

    def initialize_conditions(self):
        """Initialize the conditions collection using the supported ones from commons.Condition"""
        self.db.drop_collection(DBManager.CONDITIONS_COLLECTION)
        try:
            conditions: pymongo.collection.Collection = self.db[
                DBManager.CONDITIONS_COLLECTION
            ]
            result = conditions.insert_many(ConditionEnums.get_conditions())

            logger.info(f"Inserted {result.inserted_ids}")
        except Exception:
            logger.exception("Conditions were not initialized")


def create_mongodb_url(
    db: str, host="localhost", user=None, password=None, port: int = 27017
) -> str:
    if user and password:
        return f"mongodb://{user}:{password}@{host}:{port}/{db}"

    return f"mongodb://{host}:{port}/{db}"


def make_db_manager(url):
    connector = DBConnector(url)
    connector.connect()
    return DBManager(connector)