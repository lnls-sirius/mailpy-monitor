#!/usr/bin/env python
import typing
import logging

import pymongo
import pymongo.database
import pymongo.collection

logger = logging.getLogger("DB")


class DBConnector:
    def __init__(self, url: str, db_name: str):
        self.url = url
        self.client: typing.Optional[pymongo.MongoClient] = None
        self.db_name = db_name
        self.db: pymongo.database.Database = None

    def disconnect(self):
        """ Disconnect """
        if self.client:
            self.client.close()

    def connect(self) -> pymongo.database.Database:
        """ Estabilish mongo connection """
        self.client = pymongo.MongoClient(self.url)
        self.db: pymongo.database.Database = self.client[self.db_name]
        return self.db
