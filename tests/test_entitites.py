import queue
import unittest

from mailpy.entities.condition import ConditionEnums
from mailpy.entities.entry import AlarmEvent, Entry, EntryData, ValueChangedInfo
from mailpy.entities.group import Group


class TestEntry(unittest.TestCase):
    def test_validations(self):
        q = queue.Queue()
        g = Group("1", "gtest", True)
        entry = Entry(
            entry_data=EntryData(
                alarm_values="1:2",
                condition=ConditionEnums.OutOfRange,
                email_timeout=0,
                emails=[""],
                group=g,
                id="e1",
                pvname="TestPV",
                subject="",
                unit="",
                warning_message="",
            ),
            group=g,
            event_queue=q,
        )

        # Dispatch invalid with missmatch name
        self.assertEqual(q.qsize(), 0)
        with self.assertRaises(ValueError):
            entry.handle_value_change(
                ValueChangedInfo(
                    pvname="asd",
                    value=0,
                    status=1,
                    host="host",
                    severity=0,
                )
            )
        self.assertEqual(q.qsize(), 0)

    def test_entry_out_of_range(self):
        q = queue.Queue()

        g = Group("1", "gtest", True)
        entry = Entry(
            entry_data=EntryData(
                alarm_values="1:2",
                condition=ConditionEnums.OutOfRange,
                email_timeout=0,
                emails=[""],
                group=g,
                id="e1",
                pvname="TestPV",
                subject="",
                unit="",
                warning_message="",
            ),
            group=g,
            event_queue=q,
        )

        # Dispatch valid alarm
        entry.handle_value_change(
            ValueChangedInfo(
                pvname="TestPV",
                value=0,
                status=1,
                host="host",
                severity=0,
            )
        )
        self.assertEqual(q.qsize(), 1)
        self.assertIsInstance(q.get(), AlarmEvent)
        self.assertEqual(q.qsize(), 0)

        # Disable alarm via group
        g.enabled = False
        entry.handle_value_change(
            ValueChangedInfo(
                pvname="TestPV",
                value=0,
                status=1,
                host="host",
                severity=0,
            )
        )
        self.assertEqual(q.qsize(), 0)
