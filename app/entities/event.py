import dataclasses
import typing

from .timestamp import Timestamp


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

    ts: Timestamp = Timestamp()


def _value_to_string(value):
    if type(value) == float:
        return "{:.4}".format(value)

    return str(value)


def _check_emails(emails):
    if type(emails) == list:
        return emails
    raise ValueError(f"Invalid type for emails '{emails}', expected type {list}")


def create_event(
    pvname: str,
    specified_value_message: str,
    unit: str,
    warning: str,
    subject: str,
    emails: typing.List[str],
    condition: str,
    value_measured: any,
):

    return AlarmEvent(
        pvname=pvname,
        specified_value_message=specified_value_message,
        unit=unit,
        warning=warning,
        subject=subject,
        emails=_check_emails(emails),
        condition=condition,
        value_measured=_value_to_string(value_measured),
    )
