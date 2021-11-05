import concurrent.futures
import logging
import queue
import threading
import time
import typing

import app.db as db
import app.entities as entities
import app.helpers as helpers
import app.mail as mail

logger = logging.getLogger()

SMS_MAX_QUEUE_SIZE = 50000


class Manager:
    def __init__(self, tls: bool, login: str, passwd: str, db_url: str):

        self.sms_queue: queue.Queue = queue.Queue(maxsize=SMS_MAX_QUEUE_SIZE)

        self.entries: typing.Dict[str, entities.Entry] = {}
        self.groups: typing.Dict[str, entities.Group] = {}
        self.tick: float = 15
        self.running: bool = True

        self.db = db.make_db_manager(url=db_url)
        self.mail_client = mail.MailClient(login=login, passwd=passwd, tls=tls)

        self.main_thread_executor_workers = 1
        self.main_thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.main_thread_executor_workers,
            thread_name_prefix="SMSAction",
        )
        self.tick_thread = threading.Thread(
            daemon=False, target=self.do_tick, name="SMS Tick"
        )

    def load_from_database(self):
        """Load entries from database"""
        entries_data = self.db.get_entries()
        for entry_data in entries_data:

            # Create group if needed
            if entry_data.group not in self.groups:
                group_data: db.GroupData = self.db.get_group(entry_data.group)
                self.groups[entry_data.group] = entities.Group(
                    name=group_data.name, enabled=group_data.enabled, id=group_data.id
                )
                logger.info(f"Creating group {group_data}")

            try:
                entry = entities.Entry(
                    group=self.groups[entry_data.group],
                    sms_queue=self.sms_queue,
                    entry_data=entry_data,
                )
                entry.connect()
                self.entries[entry_data.id] = entry
                logger.info(f"Creating entry {entry}")
            except helpers.EntryException:
                logger.exception("Failed to create entry")

    def send_email(self, event: entities.AlarmEvent):
        try:
            with self.mail_client:
                self.mail_client.send_email(event)
        except Exception as e:
            logger.exception(f"Failed to send email for event '{event}'. Error {e}")

    def persist_event(self, event: entities.AlarmEvent):
        try:
            logger.info(f"@todo: Persist event {event} to database")
        except Exception as e:
            logger.exception(f"Failed to persist event {event} to database. Error {e}")

    def start(self):
        # self.main_thread.start()
        for _ in range(self.main_thread_executor_workers):
            self.main_thread_executor.submit(self.consume_alarm_events)
        self.main_thread_executor.shutdown(wait=False)

        self.tick_thread.start()

    def join(self):
        self.tick_thread.join()

    def do_tick(self):
        """Trigger Entry processing"""
        while self.running:
            time.sleep(self.tick)
            for entry in self.entries.values():
                if not self.running:
                    break
                entry.trigger()

    def consume_alarm_events(self):
        """
        Application loop: Check email targets
        """

        while self.running:
            event = self.sms_queue.get(block=True, timeout=None)

            if type(event) != entities.AlarmEvent:
                logger.warning(f"Unknown event type {event} obtained from queue.")
                continue

            # Send an email
            self.send_email(event)
            self.persist_event(event)
