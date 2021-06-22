import logging


logger = logging.getLogger("COMMONS")


class ConfigEvent:
    """Configuration event sent by the IOC to the SMS queue"""

    def __init__(
        self,
        config_type: int,
        value=None,
        pv_name: str = None,
    ):
        self.config_type = config_type
        self.value = value
        self.pv_name = pv_name

    def __str__(self):
        return f"<ConfigEvent={self.config_type} value={self.value}>"


class EmailEvent:
    """Email event sent by entry to the SMS queue to signal alarms"""

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
