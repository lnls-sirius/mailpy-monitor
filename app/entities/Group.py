import threading
import typing


class GroupData(typing.NamedTuple):
    id: str
    name: str
    enabled: bool
    description: str


class Group:
    """Group of PVs"""

    def __init__(self, id: str, name: str, enabled: bool = True, description: str = ""):
        self._enabled: bool = enabled
        self._id = id
        self.description = description
        self.lock = threading.RLock()
        self.name: str = name

    @property
    def id(self):
        return self._id

    @property
    def enabled(self):
        with self.lock:
            return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        with self.lock:
            self._enabled = value

    def __str__(self):
        return f'Group(id={self._id},name="{self.name}",enabled="{self.enabled}")'
