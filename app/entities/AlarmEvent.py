import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class AlarmEvent:
    """Email event sent by entry to the SMS queue to signal alarms"""

    pvname: str
    specified_value_message: str
    unit: str
    subject: str
    emails: typing.List[str]
    warning: str
    condition: str
    value_measured: str
