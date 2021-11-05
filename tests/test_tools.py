import datetime
import unittest

from app.entities.timestamp import Timestamp
from app.utils import MongoContainerManager


class TestToolsMongodb(unittest.TestCase):
    def test_init_database(self):
        manager = MongoContainerManager()
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
