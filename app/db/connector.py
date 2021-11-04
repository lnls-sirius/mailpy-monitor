#!/usr/bin/env python
import logging
import typing

import pymongo
import pymongo.collection
import pymongo.database

logger = logging.getLogger("DB")


class DBConnector:
    def __init__(self, url: str):
        self._url = url
        self._client: typing.Optional[pymongo.MongoClient] = None
        self._db: typing.Optional[pymongo.database.Database] = None

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
        logger.info(f"Closing database connection {self._url}")

    def connect(self) -> pymongo.database.Database:
        self._client = pymongo.MongoClient(self._url)
        self._db = self._client.get_database()
        logger.info(f"Connecting to database {self._url}")
        return self.db

    @property
    def db(self):
        if not self._client:
            self.connect()
        return self._client.get_database()
