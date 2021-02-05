class EmailEvent:
    """ Email event sent by entry to the SMS queue to signal alarms """

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
