import typing
import unittest

from mailpy.db import (
    DBManager,
    EntryData,
    GroupData,
    create_mongodb_url,
    make_db_manager,
)
from mailpy.entities.event import create_alarm_event
from mailpy.tools import MongoContainerManager, MongoJsonLoader


class TestDatabaseInteraction(unittest.TestCase):

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

            e_data = {
                "pvname": "str",
                "specified_value_message": "str",
                "unit": "str",
                "warning": "str",
                "subject": "str",
                "emails": ["anEmail"],
                "condition": "a condition",
                "value_measured": "typing.Any",
            }
            event = create_alarm_event(**e_data)
            db.persist_event(event)

    def tearDown(self):
        self.container.stop()
