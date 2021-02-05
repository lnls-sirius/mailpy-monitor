class ConfigEvent:
    """ Configuration event sent by the IOC to the SMS queue """

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
