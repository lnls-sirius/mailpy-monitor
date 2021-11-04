import datetime


class TimestampNow:
    def __init__(self) -> None:
        self._ts = datetime.datetime.now(datetime.timezone.utc)
        self._local_str = self.format_for_readers(self._ts)
        self._utc_str = self.format_for_archiver(self._ts)

    @staticmethod
    def format_for_archiver(ts: datetime.datetime):
        return ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

    @staticmethod
    def format_for_readers(ts: datetime.datetime):
        return ts.astimezone().strftime("%a, %d %b %Y %H:%M:%S %Z")

    @property
    def local_str(self):
        return self._local_str

    @property
    def utc_str(self):
        return self._utc_str

    def __str__(self):
        return f"{self._ts}"

    @property
    def ts(self):
        return self._ts
