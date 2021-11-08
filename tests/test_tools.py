import datetime
import unittest

from mailpy.entities.timestamp import Timestamp
from mailpy.utils import MongoContainerManager, MongoJsonLoader


class TestToolsMongodb(unittest.TestCase):
    def test_load_json(self):
        loader = MongoJsonLoader()
        self.assertIsNotNone(loader.load_entries())
        self.assertIsNotNone(loader.load_groups())

    def test_init_database(self):
        manager = MongoContainerManager()
        self.assertIsNotNone(manager._volumes())
        manager.start()

        manager.start()
        manager.stop()

        with MongoContainerManager():
            pass


class TestTimestamps(unittest.TestCase):
    def test_timestamp_now(self):
        now = Timestamp()

        self.assertIsInstance(now.ts, datetime.datetime)
        self.assertIsInstance(now.utc_str, str)
        self.assertIsInstance(now.local_str, str)
