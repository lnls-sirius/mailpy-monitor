import typing
import unittest

from app.db import EntryData, GroupData, make_db_manager, DBManager, create_mongodb_url
from .utils import MongoContainerManager, MongoJsonLoader


class TestMongodbInterface(unittest.TestCase):

    db: DBManager
    container: MongoContainerManager

    entries_fixture: typing.List[EntryData] = []
    groups_fixture: typing.List[GroupData] = []

    def setUp(self):
        self.start_mongodb_container()
        self.setup_fixtures_from_json()

    def setup_fixtures_from_json(self):
        loader = MongoJsonLoader()
        self.entries_fixture = loader.load_entries()
        self.groups_fixture = loader.load_groups()

    def start_mongodb_container(self):
        self.container = MongoContainerManager()
        self.container.start()

    def test_db_connection(self):
        with make_db_manager(
            url=create_mongodb_url(
                db=self.container.config.database,
                host=self.container.config.host,
                password=self.container.config.password,
                port=self.container.config.port,
                user=self.container.config.username,
            )
        ) as db:

            entries = db.get_entries()
            entries.sort(key=lambda x: x.id)

            self.assertGreater(self.entries_fixture.__len__(), 0)
            self.assertGreater(self.groups_fixture.__len__(), 0)

            for fixture, entry in zip(self.entries_fixture, entries):
                self.assertEqual(fixture, entry)

            for fixture in self.groups_fixture:
                self.assertEqual(fixture, db.get_group(fixture.name))

    def tearDown(self):
        self.container.stop()
