#!/usr/bin/env python3
import concurrent.futures
import logging
import multiprocessing
import queue
import threading
import time
import typing

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
        self._sms_queue = sms_queue

        self._entries: typing.Dict[str, commons.Entry] = {}
        self._groups: typing.Dict[str, commons.Group] = {}

        self._tick: float = 15
        self._enable: bool = True
        self._running: bool = True

        self._db = db.DBManager(url=db_url)
        self._sms_dispatcher = mail.Dispatcher(login, passwd, tls)

        self._main_thread_executor_workers = 5
        self._main_thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self._main_thread_executor_workers,
            thread_name_prefix="SMSAction",
        )
        self._tick_thread = threading.Thread(
            daemon=False, target=self.do_tick, name="SMS Tick"
        )

    def load_from_database(self):
        """Load entries from database"""
        dict_entries = self._db.get_entries()
        for d_entry in dict_entries:

            # Create group if needed
            group_name = d_entry["group"]
            if group_name not in self._groups:
                self._groups[group_name] = commons.Group(name=group_name, enabled=True)
                logger.info(f"Creating group {self._groups[group_name]}")

            try:
                _id = d_entry["_id"]
                d_entry.pop(
                    "group", None
                )  # Remove the group name as we are using the object

                self._entries[_id] = commons.Entry(
                    group=self._groups[group_name], sms_queue=self._sms_queue, **d_entry
                )
                logger.info(f"Creating entry {self._entries[_id]}")
            except commons.EntryException:
                logger.exception("Failed to create entry")

    def start(self):
        for _ in range(self._main_thread_executor_workers):
            self._main_thread_executor.submit(self.do_main_action)
        self._main_thread_executor.shutdown(wait=False)

        self._tick_thread.start()

    def join(self):
        self._tick_thread.join()

    def do_tick(self):
        """Trigger Entry processing"""
        while self._running:
            time.sleep(self._tick)
            for entry in self._entries.values():
                if not self._running:
                    break
                entry.trigger()

    def do_main_action(self):
        """
        Application loop: Check email targets
        """
        if not self._sms_dispatcher.authenticate_account():
            logger.fatal(
                "Failed to authenticate gmail mail account. SMS program shut down"
            )
            self._running = False
            return

        while self._running:
            event = self._sms_queue.get(block=True, timeout=None)

            if not self._enable:
                logger.warning("SMS is disabled")
                continue

            if type(event) == commons.EmailEvent:
                # Send an email
                message = self._sms_dispatcher.compose_msg(event)
                self._sms_dispatcher.send_email(event, message)

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
                self._enable = True if event.value else False
                logger.info(f"SMS status enable={self._enable}")

            elif event.config_type == commons.ConfigType.GetSMSState:
                pass

            elif (
                event.config_type == commons.ConfigType.SetGroupState
                or event.config_type == commons.ConfigType.GetGroupState
            ):
                group_name = event.pv_name
                if group_name not in self._groups:
                    # Invalid group
                    logger.warning(
                        f"Failed to handle {event}, {group_name} is not a valid group"
                    )
                    return

                group: commons.Group = self._groups[group_name]

                if event.config_type == commons.ConfigType.SetGroupState:

                    group.enabled = True if event.value else False
                    logger.info(f"Group {group} enabled={event.value}")

                elif event.config_type == commons.ConfigType.GetGroupState:
                    pass
            else:
                logger.error("Unsupported config event type {event}")
        except queue.Full:
            logger.exception("Cannot send information back to the IOC.")
