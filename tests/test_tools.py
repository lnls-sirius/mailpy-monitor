import unittest

from app.utils import MongoContainerManager


class TestToolsMongodb(unittest.TestCase):
    def test_init_database(self):
        manager = MongoContainerManager()
        manager.start()

        manager.start()
        manager.stop()

        with MongoContainerManager():
            pass
