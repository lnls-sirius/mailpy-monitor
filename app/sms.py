#!/usr/bin/env python3
import logging
import ssl
import threading
import multiprocessing
import queue
import time
import typing
import concurrent.futures
from time import localtime, strftime

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from . import commons
from . import db
from . import (
    ENABLE_STS,
    SMS_ENABLE_PV_STS,
    SMS_PREFIX,
)

logger = logging.getLogger("SMS")


class SMSException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class SMSApp:
    def __init__(
        self,
        tls: bool,
        login: str,
        passwd: str,
        ioc_queue: multiprocessing.Queue,
        sms_queue: multiprocessing.Queue,
        db_url: str,
    ):
        self.ioc_queue = ioc_queue
        self.sms_queue = sms_queue

        self.entries: typing.Dict[str, commons.Entry] = {}
        self.groups: typing.Dict[str, commons.Group] = {}
        self.tls: bool = tls
        self.login: str = login
        self.passwd: str = passwd
        self.tick: float = 15
        self.enable: bool = True
        self.running: bool = True

        self.db = db.DBManager(url=db_url)

        self.main_thread_executor_workers = 5
        self.main_thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.main_thread_executor_workers,
            thread_name_prefix="SMSAction",
        )
        self.tick_thread = threading.Thread(
            daemon=False, target=self.do_tick, name="SMS Tick"
        )

    def load_from_database(self):
        """ Load entries from database """
        dict_entries = self.db.get_entries()
        for d_entry in dict_entries:

            # Create group if needed
            group_name = d_entry["group"]
            if group_name not in self.groups:
                self.groups[group_name] = commons.Group(name=group_name, enabled=True)
                logger.info(f"Creating group {self.groups[group_name]}")

            try:
                _id = d_entry["_id"]
                d_entry.pop(
                    "group", None
                )  # Remove the group name as we are using the object

                self.entries[_id] = commons.Entry(
                    group=self.groups[group_name], sms_queue=self.sms_queue, **d_entry
                )
                logger.info(f"Creating entry {self.entries[_id]}")
            except commons.EntryException:
                logger.exception("Failed to create entry")

    def compose_msg(self, event: commons.EmailEvent) -> MIMEMultipart:
        """
        :param commons.EmailEvent event: Message content
        :return: body of the e-mail that will be sent
        """
        msg = MIMEMultipart("alternative")
        msg["From"] = self.login
        msg["To"] = event.emails.replace(";", ", ")
        msg["Cc"] = ""
        msg["Bcc"] = ""
        msg["Subject"] = event.subject

        timestamp = strftime("%a, %d %b %Y %H:%M:%S", localtime())

        # creating the plain-text format of the message
        text = f"""{event.warning}\n
     - PV name:         {event.pvname}
     - Specified range: {event.specified_value_message}
     - Value measured:  {event.value_measured} {event.unit}
     - Timestamp:       {timestamp}

     Archiver link: https://10.0.38.42

     Controls Group\n"""

        html = f"""\
        <html>
            <body>
                <p> {event.warning} <br>
                    <ul>
                        <li><b>PV name:         </b> {event.pvname} <br></li>
                        <li><b>Specified range: </b> {event.specified_value_message}<br></li>
                        <li><b>Value measured:  </b> {event.value_measured} {event.unit}<br></li>
                        <li><b>Timestamp:       </b> {timestamp}<br></li>
                    </ul>
                    Archiver link: <a href="https://10.0.38.42">https://10.0.38.42<a><br><br>
                    Controls Group
                </p>
            </body>
        </html>
        """

        text_part = MIMEText(text, "plain")
        html_part = MIMEText(html, "html")
        # add html/plain-text parts to MIMEMultipart message.
        # The email client will try to render the last part first (in this case the html)
        msg.attach(text_part)
        msg.attach(html_part)
        return msg

    def send_email(self, event: commons.EmailEvent, msg: MIMEMultipart):
        """
        Send an email
        :param commons.EmailEvent event: Email content specifics
        :param MIMEMultipart msg: Message content
        """
        email = event.emails.split(";")

        try:
            # Create a secure SSL context
            context = ssl.create_default_context()

            if self.tls:
                # Start an unsecured SMTP connection and then encrypt it.
                # Gmail SMTP server requires a connection with port 587 if using .starttls()
                port = 587
                # Create a secure SSL context
                # try to log in to server and send email
                with smtplib.SMTP("smtp.gmail.com", port) as server:
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                    server.login(self.login, self.passwd)
                    server.sendmail(self.login, email, msg.as_string())

            else:
                # Start a secured SMTP connection from the beginning.
                # Gmail SMTP server requires a connection with port 465 if using SMTP_SSL()
                port = 465
                with smtplib.SMTP_SSL(
                    "smtp.gmail.com", port, context=context
                ) as server:
                    server.login(self.login, self.passwd)
                    server.sendmail(self.login, email, msg.as_string())

            logger.info(f"Email sent with success. {email}")
        except ssl.SSLError:
            logger.exception("Error from the underlying SSL implementation")
        except smtplib.SMTPAuthenticationError:
            logger.exception(
                f"Failed to authenticate with username:{self.login} and password: {self.passwd}"
            )
        except smtplib.SMTPException:
            logger.exception("Error from the smtplib module")

    def authenticate_account(self) -> bool:
        """
        Authenticate gmail account
        :return bool: Successfully connected
        """
        logger.info(f"Trying to authenticate at Gmail with {self.login}")

        authentication = False
        try:
            context = ssl.create_default_context()
            while not authentication:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(self.login, self.passwd)
                    authentication = True
                    logger.info(f"logged successfully with {self.login}")
                    return True

        except ssl.SSLError:
            logger.exception("Error from the underlying SSL implementation")
        except smtplib.SMTPAuthenticationError:
            logger.exception(
                f"Failed to authenticate with username:{self.login} and password: {self.passwd}"
            )
        except smtplib.SMTPException:
            logger.exception("Error from the smtplib module")

        self.passwd = None
        return False

    def start(self):
        # self.main_thread.start()
        for i in range(self.main_thread_executor_workers):
            self.main_thread_executor.submit(self.do_main_action)
        self.main_thread_executor.shutdown(wait=False)

        self.tick_thread.start()

    def do_tick(self):
        """ Trigger Entry processing """
        while self.running:
            time.sleep(self.tick)
            for entry in self.entries.values():
                if not self.running:
                    break
                entry.trigger()

    def do_main_action(self):
        """
        Application loop: Check email targets
        """
        if not self.authenticate_account():
            logger.fatal(
                "Failed to authenticate gmail mail account. SMS program shut down"
            )
            self.running = False
            return

        while self.running:
            event = self.sms_queue.get(block=True, timeout=None)

            if not self.enable:
                logger.warning('SMS is disabled (PV "CON:MailServer:Enable" is zero)')
                continue

            if type(event) == commons.EmailEvent:
                # Send an email
                message = self.compose_msg(event)
                self.send_email(event, message)

            elif type(event) == commons.ConfigEvent:
                self.handle_config(event)

            else:
                logger.warning(f"Unknown event type {event} obtained from queue.")

    def handle_config(self, event: commons.ConfigEvent):
        """
        Handle configuration changes.
        :param commons.ConfigEvent event: Configuration event.
        """
        try:
            if event.config_type == commons.ConfigType.SetSMSState:
                self.enable = True if event.value else False

                self.ioc_queue.put(
                    {
                        "reason": SMS_ENABLE_PV_STS,
                        "value": 1 if self.enable else 0,
                    }
                )
                logger.info(f"SMS status enable={self.enable}")

            elif event.config_type == commons.ConfigType.GetSMSState:
                self.ioc_queue.put(
                    {"reason": event.pv_name, "value": 1 if self.enable else 0}
                )

            elif (
                event.config_type == commons.ConfigType.SetGroupState
                or event.config_type == commons.ConfigType.GetGroupState
            ):
                group_name = event.pv_name
                if group_name not in self.groups:
                    # Invalid group
                    logger.warning(
                        f"Failed to handle {event}, {group_name} is not a valid group"
                    )
                    return

                group: commons.Group = self.groups[group_name]

                if event.config_type == commons.ConfigType.SetGroupState:

                    group.enabled = True if event.value else False
                    self.ioc_queue.put(
                        {
                            "reason": f"{SMS_PREFIX}:{group_name}:{ENABLE_STS}",
                            "value": 1 if event.value else 0,
                        }
                    )
                    logger.info(f"Group {group} enabled={event.value}")

                elif event.config_type == commons.ConfigType.GetGroupState:

                    self.ioc_queue.put(
                        {
                            "reason": f"{SMS_PREFIX}:{group_name}:{ENABLE_STS}",
                            "value": 1 if group.enable else 0,
                        }
                    )

            else:
                logger.error("Unsupported config event type {event}")
        except queue.Full:
            logger.exception("Cannot send information back to the IOC.")
