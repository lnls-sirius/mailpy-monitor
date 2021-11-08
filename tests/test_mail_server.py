import smtplib
import unittest

from mailpy.entities.condition import ConditionEnums
from mailpy.entities.event import AlarmEvent
from mailpy.mail.client import MailClient
from mailpy.mail.message import MessageContent, compose_msg_content


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


#  def test_send_email(self):
#     event = AlarmEvent(
#          pvname="MailpyContinuousIntegrationTest",
#           specified_value_message="Out of range!!!",
#           unit="U",
#           subject="Mailpy: Continuous Integration Test",
#           emails=[os.environ.get("EMAIL_USER")],
#            warning="",
#            value_measured="-100",
#            condition=ConditionEnums.InferiorThan,
#        )
#        with MailClient(
#            debug_level=1,
#            login=os.environ.get("EMAIL_USER"),
#            passwd=os.environ.get("EMAIL_PASSWORD"),
#            tls=False,
#        ) as client:
#            client.send_email(event=event)
