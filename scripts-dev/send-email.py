#!/usr/bin/env python
from mailpy.entities.condition import ConditionEnums
from mailpy.entities.event import create_alarm_event
from mailpy.mail.client import MailClient, Settings


if __name__ == "__main__":

    event_fixture = create_alarm_event(
        pvname="ThisPvDoesNotExist",
        specified_value_message="Testing the new email configuration",
        unit="U",
        subject="MailPy Test - Email notification",
        emails=["claudio.carneiro@cnpem.br", "claudiofcarneiro@gmail.com"],
        warning="",
        value_measured="-100",
        condition=ConditionEnums.InferiorThan,
    )

    with MailClient(
        debug_level=2,
        login="gas-noreply@cnpem.br",
        passwd="",
        host=Settings.CNPEM_HOSTNAME,
        port=Settings.CNPEM_TLS_PORT,
        tls=True,
    ) as client:
        client.send_email(event=event_fixture)
