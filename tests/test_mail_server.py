import smtplib
import unittest

from app.entities.AlarmEvent import AlarmEvent
from app.entities.Condition import ConditionEnums
from app.mail.client import MailClient
from app.mail.message import MessageContent, compose_msg_content


class TestMailClient(unittest.TestCase):
    event_fixture = AlarmEvent(
        pvname="TEST:PV",
        specified_value_message="Out of range!!!",
        unit="U",
        subject="",
        emails=["test@email.com", "test2@mail.com"],
        warning="",
        value_measured="-100",
        condition=ConditionEnums.InferiorThan,
    )

    def test_create_message(self):
        message = compose_msg_content(self.event_fixture)
        self.assertIsInstance(message, MessageContent)
        self.assertIsInstance(message.text, str)
        self.assertIsInstance(message.html, str)

    def test_client_tls(self):
        with self.assertRaises(ValueError):
            with MailClient(
                debug_level=2,
                login="rando",
                passwd="some passwd",
                tls=True,
                host="smtp.gmail.com",
            ) as client:
                client.send_email(event=self.event_fixture)

    def test_client_ssl(self):
        with self.assertRaises(smtplib.SMTPAuthenticationError):
            with MailClient(
                debug_level=2,
                login="rando",
                passwd="some passwd",
                tls=False,
            ) as client:
                client.send_email(event=self.event_fixture)
