import queue
import threading
import time
import typing

import mailpy.logging as logging

from .condition import Condition, create_condition
from .event import AlarmEvent, create_alarm_event
from .group import Group

logger = logging.getLogger()


class ConnectionChangedInfo(typing.NamedTuple):
    pvname: str
    conn: bool


#       "pvname": "LA-CN:H1MPS-1:A2Temp2",
#       "value": 0.0,
#       "status": 17,
#       "ftype": 20,
#       "host": "172.25.184.177:5064",
#       "severity": 3,
#       "timestamp": 1636134688.979506,
#       "posixseconds": 1636134688.0,
#       "nanoseconds": 979506600,
#       "precision": None,
#       "units": None,
#       "enum_strs": None,
#       "upper_disp_limit": None,
#       "lower_disp_limit": None,
#       "upper_alarm_limit": None,
#       "lower_alarm_limit": None,
#       "lower_warning_limit": None,
#       "upper_warning_limit": None,
#       "upper_ctrl_limit": None,
#       "lower_ctrl_limit": None,
#       "nelm": 1,
#       "type": "time_double",
class ValueChangedInfo(typing.NamedTuple):
    pvname: str
    value: typing.Any
    status: int
    host: str
    severity: int


class EntryData(typing.NamedTuple):
    id: str
    pvname: str
    emails: typing.List[str]
    condition: str
    alarm_values: str
    unit: str
    warning_message: str
    subject: str
    email_timeout: float
    group: str


class Entry:
    def __init__(
        self,
        group: Group,
        entry_data: EntryData,
        event_queue: queue.Queue,
    ):
        self._value_callback_id: typing.Optional[int] = None
        self._connection_callback_id: typing.Optional[int] = None

        self._id = entry_data.id
        self._pvname = entry_data.pvname

        self._condition: Condition = create_condition(
            condition=entry_data.condition.lower().strip(),
            alarm_values=entry_data.alarm_values,
        )

        self._sms_queue_dispatch_lock = threading.RLock()

        self.email_timeout = entry_data.email_timeout
        self.emails = entry_data.emails
        self.group = group
        self.event_queue = event_queue
        self.subject = entry_data.subject
        self.unit = entry_data.unit
        self.warning_message = entry_data.warning_message

        # reset last_event_time for all PVs, so it start monitoring right away
        self.last_event_time = time.time() - self.email_timeout

    @property
    def pvname(self):
        return self._pvname

    @property
    def alarm_values(self):
        return self._condition.alarm_values

    @property
    def condition(self):
        return self._condition.name

    @property
    def id(self):
        return self._id

    def handle_condition(self, value) -> typing.Optional[AlarmEvent]:
        """
        Handle the alarm condition and return an post a request to the SMS queue.
        """
        cond_res = self._condition.check_alarm(value)
        if not cond_res:
            return None

        return create_alarm_event(
            pvname=self.pvname,
            specified_value_message=cond_res.message,
            unit=self.unit,
            warning=self.warning_message,
            subject=self.subject,
            emails=self.emails,
            condition=self.condition,
            value_measured=value,
        )

    def is_timeout_active(self):
        timestamp = time.time()
        timedelta = timestamp - self.last_event_time
        return timedelta < self.email_timeout

    def handle_connection_change(self, data: ConnectionChangedInfo):
        if self.pvname != data.pvname:
            logger.warning(
                f"{self} received a wrong connection_change event from pv {data.pvname}"
            )
            return

        if data.conn:
            logger.info(f"PV {data.pvname} reconnected")
            return

        logger.warning(f"PV {data.pvname} has disconnected")

        # @todo: Consider dispatching an alarm to the queue

    def handle_value_change(self, data: ValueChangedInfo):
        """
        Define if an alarm check should be performed. Disconnected PVs will are not checked.
        Trigger this function as a callback and within a timer due to the sms timeout. e.g.: Callback may be ignored.
        :return bool: Perform or not the alarm check.
        """
        if not self.group.enabled:
            logger.debug(f"Ignoring {self} due to disabled group")
            return

        if self.is_timeout_active():
            logger.info(f"Ignoring event from {self}, timeout still active.")
            return

        if data.value is None:
            return

        event = self.handle_condition(data.value)
        if not event:
            return

        if data.pvname != self.pvname:
            raise ValueError(
                f"Cannot complete eveent handling, received valud changed event PV ({data}) differs from entry PV ({self})"
            )

        self.dispatch_alarm_event(event)

    def dispatch_alarm_event(self, event: AlarmEvent):
        if not event:
            logger.error(f"Cannot dispatch empty event {event} from entry {self}")
            return

        try:
            with self._sms_queue_dispatch_lock:  # Lock used to maintain the last_event_time in sync with the queue
                logger.info(f"New event '{event}' being dispatched from {self}")
                self.event_queue.put(event, block=False, timeout=None)
                self.last_event_time = time.time()

        except queue.Full:
            logger.exception(
                f"Failed to put entry in queue {self} {event}. Queue is full, something wrong is happening..."
            )

    def __str__(self):
        return f'Entry({self.id},"{self.pvname}","{self.condition}",{self.group.name},"{self.alarm_values}",{self.emails}>'
