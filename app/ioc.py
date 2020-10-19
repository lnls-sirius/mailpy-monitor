import threading
import queue
import logging

import pcaspy

from . import commons
from . import sms
from . import SMS_QUEUE

logger = logging.getLogger("IOC")

SMS_ENABLE_PV = "CON:MailServer:Enable"
DBD_ON_OFF = {
    "type": "enum",
    "enums": ["Off", "On"],
    "value": 1,
}


class SMSEpicsDriver(pcaspy.Driver):
    def __init__(self, sms_app: sms.SMSApp):
        super().__init__()
        # @todo: Consider not passing sms.SMSApp.
        self.sms_app = sms_app
        self.pvdb = {}
        self.create_pvdb()

    def create_pvdb(self):
        # create general PV to enable/disable the whole SMS
        self.pvdb[SMS_ENABLE_PV] = {
            "type": "enum",
            "enums": ["Off", "On"],
            "value": 1,
        }
        for pv, value in self.sms_app.groups.items():
            self.pvdb[pv] = {
                "type": "enum",
                "enums": ["Off", "On"],
                "value": 1 if value.enabled else 0,
            }

    def complete_transaction(self, reason, value):
        self.setParam(reason, value)
        self.updatePVs()

    def write(self, reason: str, value):
        try:
            if reason == SMS_ENABLE_PV:
                event = commons.ConfigEvent(
                    config_type=commons.ConfigType.DisableSMS,
                    value=value,
                    pv_name=reason,
                    success_callback=self.complete_transaction,
                )
                SMS_QUEUE.put(event)

            elif reason in self.sms_app.groups:
                event = commons.ConfigEvent(
                    config_type=commons.ConfigType.DisableGroup,
                    value=value,
                    pv_name=reason,
                    success_callback=self.complete_transaction,
                )
                SMS_QUEUE.put(event)

            else:
                # @todo: Handle invalid PV names?
                logger.warning(f"Support for {reason} not done yet")
                return False

            return True
        except queue.Full:
            logger.exception(f"Failed to push to command to queue {reason}")
            return False


class SMSEpicsServer:
    def __init__(self, driver: SMSEpicsDriver):
        self.driver = driver
        self.thread = threading.Thread(
            target=self.process, daemon=False, name="IOC CA Process"
        )
        self.running = False
        self.server = pcaspy.SimpleServer()
        self.server.createPV("", self.driver.pvdb)

    def process(self):
        """ Process CA transactions """
        while self.running:
            self.server.process(0.1)

    def start(self):
        """ Start IOC Server """
        self.running = True
        self.thread.start()
