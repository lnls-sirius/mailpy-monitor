#!/usr/bin/env python3
import logging
import threading
import multiprocessing
import queue
import time
import typing
import concurrent.futures

from . import commons, db, mail

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
        sms_queue: multiprocessing.Queue,
        db_url: str,
    ):
        self.sms_queue = sms_queue

        self.entries: typing.Dict[str, commons.Entry] = {}
        self.groups: typing.Dict[str, commons.Group] = {}
        self.tick: float = 15
        self.enable: bool = True
        self.running: bool = True

        self.db = db.DBManager(url=db_url)
        self.sms_dispatcher = mail.Dispatcher(login, passwd, tls)

        self.main_thread_executor_workers = 5
        self.main_thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.main_thread_executor_workers,
            thread_name_prefix="SMSAction",
        )
        self.tick_thread = threading.Thread(
            daemon=False, target=self.do_tick, name="SMS Tick"
        )

    def load_from_database(self):
        """Load entries from database"""
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

    def start(self):
        for _ in range(self.main_thread_executor_workers):
            self.main_thread_executor.submit(self.do_main_action)
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

    def do_main_action(self):
        """
        Application loop: Check email targets
        """
        if not self.sms_dispatcher.authenticate_account():
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
                message = self.sms_dispatcher.compose_msg(event)
                self.sms_dispatcher.send_email(event, message)

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
                logger.info(f"SMS status enable={self.enable}")

            elif event.config_type == commons.ConfigType.GetSMSState:
                pass

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
                    logger.info(f"Group {group} enabled={event.value}")

                elif event.config_type == commons.ConfigType.GetGroupState:
                    pass
            else:
                logger.error("Unsupported config event type {event}")
        except queue.Full:
            logger.exception("Cannot send information back to the IOC.")
