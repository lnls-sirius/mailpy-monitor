import datetime
import typing


class Timestamp:
    def __init__(self, now: typing.Optional[datetime.datetime] = None) -> None:
        if not (now is None) and type(now) != datetime.date:
            raise ValueError(
                f"Invalid input now '{now}', required type {datetime.datetime}"
            )
        self._ts = datetime.datetime.now(datetime.timezone.utc) if now is None else now
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

    @property
    def ts(self):
        return self._ts

    def __str__(self):
        return f"{self._ts}"
