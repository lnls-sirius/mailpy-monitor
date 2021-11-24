import queue
import threading

import mailpy.entities as entities
import mailpy.logging as logging
import mailpy.mail as mail
from mailpy.db import DBManager

logger = logging.getLogger()


class BaseEventConsumer:
    def __init__(self, name="EventConsumer") -> None:
        self.queue: queue.Queue = queue.Queue()
        self._thread = threading.Thread(target=self._consume, daemon=True, name=name)
        self._running = False

    def join(self):
        self._running = False
        self._thread.join()

    def start(self):
        if not self._thread.is_alive():
            self._running = True
            self._thread.start()
            logger.info(f"Consumer {self} {self._thread.name} starting")

    def handle(self, obj):
        raise NotImplementedError("Parent should implement this method")

    def _consume(self):
        while self._running:
            try:
                self.handle(self.queue.get(block=True))
            except Exception as e:
                logger.exception(f"Failed to consume event. Error '{e}'")

    def add(self, obj):
        try:
            self.queue.put(obj)
        except queue.Full:
            logger.exception(
                f"Failed to add object '{obj}' to queue. Is the consumer still running?"
            )


class EmailConsumer(BaseEventConsumer):
    def __init__(self, login: str, passwd: str, tls: bool) -> None:
        super().__init__(name="EmailConsumer")
        self.mail_client = mail.MailClient(
            login=login, passwd=passwd, tls=tls, debug_level=0
        )

    def handle(self, obj):
        if type(obj) == entities.AlarmEvent:
            self.send_email(obj)
        else:
            logger.error(
                f"Email consumer received an unsupported event '{obj}', type {type(obj)}"
            )

    def send_email(self, event: entities.AlarmEvent):
        try:
            with self.mail_client:
                self.mail_client.send_email(event)
        except Exception as e:
            logger.exception(f"Failed to send email for event '{event}'. Error {e}")


class PersistenceConsumer(BaseEventConsumer):
    def __init__(self, db_manager: DBManager) -> None:
        super().__init__(name="PersistenceConsumer")
        self.db_manager = db_manager

    def handle(self, obj):
        if isinstance(obj, entities.Event):
            self.persist_event(obj)
        else:
            logger.error(
                f"PersistenceConsumer received an unsupported event '{obj}', type {type(obj)}"
            )

    def persist_event(self, event: entities.Event):
        try:
            self.db_manager.persist_event(event=event)
        except Exception as e:
            logger.exception(f"Failed to persist event {event} to database. Error {e}")
