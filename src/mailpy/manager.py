import dataclasses
import queue
import threading
import time
import typing

import mailpy.consumer as consumer
import mailpy.data_connector as data_connector
import mailpy.db as db
import mailpy.entities as entities
import mailpy.logging as logging

logger = logging.getLogger()

EVENT_QUEUE_SIZE = 50000


@dataclasses.dataclass(frozen=True)
class Config:
    db_connection_string: str
    email_login: str
    email_password: str
    email_tls_enabled: bool = False


class Manager:
    def __init__(self, config: Config):

        self.event_queue: queue.Queue = queue.Queue(maxsize=EVENT_QUEUE_SIZE)

        self.entries: typing.Dict[str, entities.Entry] = {}
        self._tick: float = 15
        self._running: bool = True

        self.db = db.make_db_manager(url=config.db_connection_string)
        self.data_connector = data_connector.DataConnector(self.db, self.event_queue)

        self._tick_thread = threading.Thread(
            daemon=False,
            name="EPICS Tick",
            target=self._do_tick,
        )
        self._event_dispatcher_thread = threading.Thread(
            daemon=True,
            name="Event Dispatcher",
            target=self._event_dispatcher,
        )

        self.consumers: typing.List[consumer.BaseEventConsumer] = [
            consumer.PersistenceConsumer(),
            consumer.EmailConsumer(
                login=config.email_login,
                passwd=config.email_password,
                tls=config.email_tls_enabled,
            ),
        ]

    def _start_consumers(self):
        for c in self.consumers:
            c.start()

    def _consume(self, obj):
        for c in self.consumers:
            c.add(obj)

    def initialize_entries_from_database(self):
        """Load entries from database"""
        entries_data = self.db.get_entries()
        for entry_data in entries_data:
            self.data_connector.create_entry(entry_data=entry_data)

    def start(self):
        self._start_consumers()
        self._tick_thread.start()
        self._event_dispatcher_thread.start()

    def join(self):
        self._tick_thread.join()
        self._event_dispatcher_thread.join()

    def _do_tick(self):
        """Trigger Entry processing"""
        while self._running:
            time.sleep(self._tick)
            self.data_connector.tick()

    def _event_dispatcher(self):
        while self._running:
            event = self.event_queue.get(block=True, timeout=None)

            if type(event) != entities.AlarmEvent:
                logger.warning(f"Unknown event type {event} obtained from queue.")
                continue

            self._consume(event)
