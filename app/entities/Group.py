import threading


class Group:
    """ Group of PVs """

    def __init__(self, name: str, enabled: bool = True):
        self.name: str = name
        self._enabled: bool = enabled
        self.lock = threading.RLock()

    @property
    def enabled(self):
        with self.lock:
            return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        with self.lock:
            self._enabled = value

    def __str__(self):
        return f'<Group="{self.name}" enabled={self.enabled}>'

    def as_dict(self):
        return {"name": self.name, "enabled": self.enabled}
