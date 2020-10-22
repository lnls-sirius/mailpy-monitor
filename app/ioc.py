import threading
import queue
import multiprocessing
import logging
import typing

import pcaspy

from . import commons
from . import (
    ENABLE_SEL,
    ENABLE_STS,
    SMS_ENABLE_PV_SEL,
    SMS_ENABLE_PV_STS,
    SMS_PREFIX,
)

logger = logging.getLogger("IOC")

SMS_PROPERTIES = SMS_PREFIX + ":Properties-Cte"
DBD_ON_OFF = {
    "type": "enum",
    "enums": ["Off", "On"],
    "value": 1,
}


class SMSEpicsDriver(pcaspy.Driver):
    def __init__(
        self,
        groups: typing.Set[str],
        ioc_queue: multiprocessing.Queue,
        sms_queue: multiprocessing.Queue,
    ):
        super().__init__()

        self.groups = groups
        self.ioc_queue = ioc_queue
        self.sms_queue = sms_queue
        self.running = False
        self.consumer_thread = threading.Thread(
            name="Consumer", daemon=False, target=self.consumer
        )

    def start(self):
        """ Start driver threads """
        logger.info("SMSEpicsDriver starting")
        self.running = True
        self.consumer_thread.start()

    def join(self):
        """ Join driver threads """
        self.consumer_thread.join()

    def consumer(self):
        """ Consume response from another process and update the IOC """
        logger.info("SMSEpicsDriver consumer thread starting")
        while self.running:
            try:
                data = self.ioc_queue.get(block=True, timeout=None)
                if type(data) != dict:
                    logger.error("Invalid type of {data}")
                    continue

                self.setParam(**data)
                self.updatePVs()

            except queue.Empty:
                logger.exception("Failed to obtain data from IOC queue")
        logger.fatal("SMSEpicsDriver queue consumer shut down")

    def write(self, reason: str, value):
        """ EPICS write requests """
        try:
            event = None
            comps = reason.split(":")

            if reason == SMS_ENABLE_PV_SEL:  # On/Off Application
                event = commons.ConfigEvent(
                    config_type=commons.ConfigType.SetSMSState,
                    value=value,
                    pv_name=reason,
                )

            elif (
                comps.__len__() == 3
                and comps[1] in self.groups
                and comps[2] == ENABLE_SEL
            ):  # On/Off PV groups
                # comps[1] in this case is the group name
                event = commons.ConfigEvent(
                    config_type=commons.ConfigType.SetGroupState,
                    value=value,
                    pv_name=comps[1],
                )

            else:
                # @todo: Handle invalid PV names?
                logger.warning(f"Support for {reason} not done yet")
                return False

            self.sms_queue.put(event)
            self.setParam(reason, value)
            self.updatePVs()
            return True
        except queue.Full:
            logger.exception(f"Failed to push to command to queue {reason}")
            return False


class SMSEpicsServer:
    def __init__(
        self,
        groups: typing.Dict[str, int],
        ioc_queue: multiprocessing.Queue,
        sms_queue: multiprocessing.Queue,
    ):
        self.ioc_queue = ioc_queue
        self.sms_queue = sms_queue
        self.groups = set()
        self.running = False

        self.thread = threading.Thread(
            target=self.process, daemon=False, name="IOC CA Process"
        )
        self.server = pcaspy.SimpleServer()

        self.pvdb = {}
        self.create_pvdb(groups)

        self.server.createPV("", self.pvdb)

        self.driver = SMSEpicsDriver(
            groups=set(self.groups), ioc_queue=self.ioc_queue, sms_queue=self.sms_queue
        )

    def create_pvdb(self, groups):
        """ create general PV to enable/disable the whole SMS """

        # SMS On/Off
        self.pvdb[SMS_ENABLE_PV_SEL] = {
            "type": "enum",
            "enums": ["Off", "On"],
            "value": 1,
        }
        self.pvdb[SMS_ENABLE_PV_STS] = {
            "type": "enum",
            "enums": ["Off", "On"],
            "value": 1,
        }

        # Groups On/Off
        for group, value in groups.items():
            pv_sp = f"{SMS_PREFIX}:{group}:{ENABLE_SEL}"
            pv_rb = f"{SMS_PREFIX}:{group}:{ENABLE_STS}"

            self.groups.add(group)

            # Initialize Sts and Sel
            self.pvdb[pv_sp] = {
                "type": "enum",
                "enums": ["Off", "On"],
                "value": 1 if value else 0,
            }
            self.pvdb[pv_rb] = {
                "type": "enum",
                "enums": ["Off", "On"],
                "value": 1 if value else 0,
            }

        # Properties-Cte: Display all propeties of interest
        properties = []
        for pv in self.pvdb.keys():
            properties.append(pv.split(":", maxsplit=1)[-1])
        properties_str = " ".join(properties)
        self.pvdb[SMS_PROPERTIES] = {
            "type": "char",
            "value": properties_str,
            "count": len(properties_str),
        }
        logger.info(f"Properties PV {SMS_PROPERTIES} {properties}")

    def process(self):
        """ Process CA transactions """
        while self.running:
            self.server.process(0.1)

    def start(self):
        """ Start IOC Server """
        logger.info("IOC Starting")
        self.running = True
        self.thread.start()
        self.driver.start()

        self.thread.join()
        self.driver.join()

        logger.info("IOC Shutdown")


def start_ioc(
    groups: typing.Dict[str, int],
    sms_queue: multiprocessing.Queue,
    ioc_queue: multiprocessing.Queue,
):
    server = SMSEpicsServer(groups=groups, sms_queue=sms_queue, ioc_queue=ioc_queue)
    server.start()
    # Loop until completion
    server.thread.join()
