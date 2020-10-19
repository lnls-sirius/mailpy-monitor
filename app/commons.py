import time
import typing
import epics
import logging
import queue
import threading

from . import SMS_QUEUE

logger = logging.getLogger("COMMONS")


class Condition(object):
    OutOfRange = "out of range"
    SuperiorThan = "if superior than"
    InferiorThan = "if inferior than"
    IncreasingStep = "increasing step"
    DecreasingStep = "decreasing step"


class ConfigType(object):
    DisableSMS = 0
    DisableGroup = 1


class Group:
    def __init__(self, pvname: str, enabled: bool = True):
        self.pvname: str = pvname
        self._enabled: bool = enabled
        self.lock = threading.RLock()

    @property
    def enabled(self):
        with self.lock:
            return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        with self.lock:
            self.enabled = value

    def __str__(self):
        return f"<Group={self.pvname} enabled={self.enabled}>"


class EntryException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class ConfigEvent:
    def __init__(
        self,
        config_type: int,
        value,
        pv_name: str = None,
        success_callback: typing.Callable[[str, int], None] = None,
    ):
        self.config_type = config_type
        self.value = value
        self.success_callback = success_callback
        self.pv_name = pv_name

    def complete_transaction(self, new_value):
        if self.pv_name and self.success_callback:
            self.success_callback(self.pv_name, new_value)

    def __str__(self):
        return f"<ConfigEvent={self.config_type} value={self.value}>"


class EmailEvent:
    def __init__(
        self,
        pvname,
        specified_value_message,
        unit,
        subject,
        emails,
        warning,
        condition,
        value_measured,
    ):
        self.pvname = pvname
        self.specified_value_message = (
            specified_value_message  # String representing the specified value
        )
        self.unit = unit
        self.subject = subject
        self.emails = emails
        self.warning = warning
        self.condition = condition
        self.value_measured = value_measured

    def __str__(self):
        return f"<EmailEvent {self.pvname} {self.specified_value_message} {self.subject} {self.emails} {self.warning}>"


class Entry:
    def __init__(
        self,
        pvname: str,
        emails: str,
        condition: str,
        alarm_values: str,
        unit: str,
        warning_message: str,
        subject: str,
        email_timeout: float,
        group: Group,
    ):
        self.pv: epics.PV = epics.PV(pvname=pvname)
        self.pv.add_callback(self.check_alarms)

        self.condition = condition.lower().strip()
        self.alarm_values = alarm_values
        self.unit = unit
        self.warning_message = warning_message
        self.subject = subject
        self.email_timeout = email_timeout
        self.emails = emails
        self.group = group
        self.lock = threading.RLock()

        # reset last_event_time for all PVs, so it start monitoring right away
        self.last_event_time = time.time() - self.email_timeout

        if self.condition == Condition.OutOfRange:
            self.__init_out_of_range__()
        elif self.condition == Condition.SuperiorThan:
            self.__init_superior_than()
        elif self.condition == Condition.InferiorThan:
            self.__init_inferior_than()
        elif self.condition == Condition.DecreasingStep:
            # @todo:Condition not supported
            pass
        elif self.condition == Condition.IncreasingStep:
            self.__init_increasing_step__()

        self.step_level: int = 0  # Actual level
        self.step_values: typing.List[float] = []  # Step value according to level

    def __init_out_of_range__(self):
        _min, _max = self.alarm_values.split(":")
        self.alarm_min = float(_min)
        self.alarm_max = float(_max)
        if self.alarm_min >= self.alarm_max:
            raise EntryException(
                f"Cannot create entry for {self.pv.pvname} with values {self.alarm_values}. Min must be lesser than max"
            )

    def __init_superior_than(self):
        self.alarm_max = float(self.alarm_values)

    def __init_inferior_than(self):
        self.alarm_min = float(self.alarm_values)

    def __init_increasing_step__(self):
        """
        create two dictionaries, "step_level" and "step":
         -------------------------------------------------------------------------
         * step_level:
             - keys: [int] indexes that contain the 'increasing step' condition
             - values: [int] represent the current step in the stair, where 0 is
                       the lowest level, and len(step[i]) is highest level
            e.g.:
               value = '1.5:2.0:2.5:3.0'
               step  = [1.5,2.0,2.5,3.0]
               len(step) = 4

               3.0 _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _  ___Level_4___
               2.5 _ _ _ _ _ _ _ _ _ _ _ _ _ _ __L3__|
               2.0 _ _ _ _ _ _ _ _ _ _  __L2__|
               1.5 _ _ _ _ _ _ _ __L1__|
                                |
                                |
                 0 ___Level_0___|

              -Level 0: lowest level, 0 ~ 1.5 u (normal operation)
                 ...
              -Level 4: highest level, 3.0+

          obs.: emails are only sent when moving from any level to a higher one
         -------------------------------------------------------------------------
         * step:
             - keys: [int] indexes that contain the 'increasing step' condition
             - values: [array of float] represent the steps that triggers mailing
        """
        self.step_level = 0  # Current step level
        self.step_values = [
            float(val) for val in self.alarm_values.split(":")
        ]  # Step level border

        s = self.step_values[0]
        for v in self.step_level[1:]:
            if s >= v:
                raise EntryException(
                    f"Failed to crate entry for {self.pv.pvname}, step values {self.alarm_values} are not sorted"
                )
            s = v
        self.min_level = 0
        self.max_level = len(self.step_values)

    def __str__(self):
        return f"<Entry={self.pv.pvname} group={self.group} condition={self.condition}>"

    def find_next_level(self, value) -> int:
        loop_level = 0
        for step_value in self.step_values:
            # Locate the next level we belong
            if value < step_value:
                # If the value is lesser than the next level beginning, we found our current level
                return loop_level
            loop_level += 1

    def handle_condition(self, value):
        """
        Handle the alarm condition and return an post a request to the SMS queue.
        """
        specified_value_message: typing.Optional[str] = None

        if self.condition == Condition.OutOfRange and (
            value < self.alarm_min or value > self.alarm_max
        ):
            specified_value_message = (
                f"from {self.alarm_min}{self.unit} to {self.alarm_max} {self.unit}"
            )

        elif self.condition == Condition.SuperiorThan and value > self.alarm_max:
            specified_value_message = f"lower than {self.alarm_min}{self.unit}"

        elif self.condition == Condition.InferiorThan and value < self.alarm_min:
            specified_value_message = f"higher than {self.alarm_min}{self.unit}"

        elif self.condition == Condition.IncreasingStep:
            next_step_limiar = self.step_values[self.step_level]
            if value >= next_step_limiar and (self.step_level + 1) <= self.max_level:
                # We are going up levels
                loop_level = self.find_next_level(value)
                self.step_level = loop_level
                specified_value_message = f"lower than {self.step_values[0]}{self.unit}"

            if value >= next_step_limiar and self.step_level == self.max_level:
                # We are already at the maximum level
                return

            if value < next_step_limiar and self.step_level == self.min_level:
                # We are already at the lowest level
                return

            if (
                value < next_step_limiar
                and self.step_level != self.min_level
                and value < self.step_values[self.step_level - 1]
            ):
                # Going down levels
                loop_level = self.find_next_level(value)
                logger.info(
                    f"{self} going down from level {self.step_level} to {loop_level}"
                )
                self.step_level = loop_level
                return

        else:
            # @todo:Condition not supported "elif self.condition == Condition.DecreasingStep:"
            logger.error(f"Invalid condition for {self}")
            return

        event: typing.Optional[EmailEvent] = None

        try:
            if not specified_value_message:
                raise EntryException(
                    f"Something wrong happened, no specified message for entry {self}"
                )

            event = EmailEvent(
                pvname=self.pv.pvname,
                specified_value_message=specified_value_message,
                unit=self.unit,
                warning=self.warning_message,
                subject=self.subject,
                emails=self.emails,
                condition=self.condition,
                value_measured=str(value),
            )
            SMS_QUEUE.put(event, block=False, timeout=None)

        except EntryException:
            logger.exception(f"Invalid entry {self}")

        except queue.Full:
            logger.exception(
                f"Failed to put entry in queue {self} {event}. Queue is full, something wrong is happening..."
            )

    def trigger(self):
        """ Manual trigger """
        self.check_alarms(value=self.pv.value)

    def check_alarms(self, **kwargs):
        """
        Define if an alarm check should be performed. Disconnected PVs will are not checked.
        Trigger this function as a callback and within a timer due to the sms timeout. e.g.: Callback may be ignored.
        :return bool: Perform or not the alarm check.
        """
        if not self.group.enabled:
            logger.info(f"Ignoring {self} due to disabled group")
            return

        if not self.pv.connected:
            logger.warning(f"Ignoring {self}, PV is disconnected")
            return

        timestamp = time.time()
        timedelta = timestamp - self.last_event_time
        if timedelta < self.email_timeout:
            logger.info(
                "Ignoring {}, timeout still active for {:.2}s".format(self, timedelta)
            )
            return

        with self.lock:
            self.last_event_time = timestamp
            self.handle_condition(value=kwargs["value"])
