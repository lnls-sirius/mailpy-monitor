import queue
import typing

import epics

import mailpy.db as db
import mailpy.entities as entities
import mailpy.helpers as helpers
import mailpy.logging as logging
from mailpy.entities.group import Group

logger = logging.getLogger()


class EpicsConnector:
    def __init__(self, pvname: str):
        self._pv = epics.PV(
            pvname,
            connection_callback=self._dispatch_connection_changed_event,
            callback=self._dispatch_value_changed_event,
        )
        if not self._pv.connected:
            logger.warning(f"Epics PV {self._pv} is disconnected")
        self._entries: typing.Set[entities.Entry] = set()

    def _dispatch_value_changed_event(self, *_args, **kwargs):
        data = entities.ValueChangedInfo(
            pvname=kwargs.get("pvname", None),
            value=kwargs.get("value", None),
            status=kwargs.get("status", None),
            host=kwargs.get("host", None),
            severity=kwargs.get("severity", None),
        )
        for entry in self._entries:
            try:
                entry.handle_value_change(data)
            except Exception as e:
                logger.exception(
                    f"Failed to dispatch event '{data}' for entry '{entry}', error {e}"
                )

    def _dispatch_connection_changed_event(self, *_args, **kwargs):
        data = entities.ConnectionChangedInfo(
            pvname=kwargs["pvname"],
            conn=kwargs["conn"],
        )
        for entry in self._entries:
            entry.handle_connection_change(data)

    def _has_entry(self, entry):
        return entry in self._entries

    def add_entry(self, entry: entities.Entry):
        if type(entry) != entities.Entry:
            raise ValueError(f"Invalid type for entry {type(entry)}")
        if self._has_entry(entry):
            return

        self._entries.add(entry)

    def tick(self):
        self._pv.run_callbacks()


class DataConnector:
    def __init__(self, db: db.DBManager, event_queue: queue.Queue):
        self._connectors: typing.Dict[str, EpicsConnector] = {}
        self._groups: typing.Dict[str, entities.Group] = {}
        self._db = db
        self._queue = event_queue

    def _add_connector(self, pvname: str):
        if not (pvname in self._connectors):
            self._connectors[pvname] = EpicsConnector(pvname)
        return self._connectors[pvname]

    def tick(self):
        for _, c in self._connectors.items():
            c.tick()

    def create_entry(self, entry_data: entities.EntryData):
        # Create group if needed
        if not (entry_data.group in self._groups):
            group_data: db.GroupData = self._db.get_group(entry_data.group)
            self._groups[entry_data.group] = entities.Group(
                name=group_data.name, enabled=group_data.enabled, id=group_data.id
            )
            logger.info(f"Creating group {group_data}")

        try:
            self.add_entry(
                entities.Entry(
                    group=self._groups[entry_data.group],
                    entry_data=entry_data,
                    event_queue=self._queue,
                )
            )
            logger.info(f"Creating entry {entry_data}")
        except helpers.EntryException:
            logger.exception("Failed to create entry")

    def add_entry(self, entry: entities.Entry):
        connector = self._add_connector(pvname=entry.pvname)
        connector.add_entry(entry)
        self.add_group(entry.group)

    def add_group(self, group: entities.Group):
        if type(group) == Group and not (group.name in self._groups):
            self._groups[group.name] = group
