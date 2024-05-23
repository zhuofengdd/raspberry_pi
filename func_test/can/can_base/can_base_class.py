import can
import time
import logging
from threading import Lock
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class CanBaseClass(ABC):
    def __init__(self):
        self.listeners = [MessageListener(self)]
        self.notifier = None
        self.buffer = can.BufferedReader()
        self.send_lock = Lock()
        self.bus = None

    def connect(self, *args, **kwargs):
        try:
            self.bus = can.ThreadSafeBus(*args, **kwargs)
            logger.info("Connected to '%s'", self.bus.channel_info)
            self.notifier = can.Notifier(self.bus, self.listeners, 1)
        except Exception as e:
            logger.error(f"Error connecting to CAN bus: {e}")
            raise
        return self

    def disconnect(self):
        try:
            if self.notifier:
                self.notifier.stop()
            if self.bus:
                self.bus.shutdown()
                self.bus = None
            self.check()
        except Exception as e:
            logger.error(f"Error disconnecting from CAN bus: {e}")

    def send_message(self, identifier, data):
        if not self.bus:
            raise RuntimeError("Not connected to CAN bus")
        msg = can.Message(
            is_extended_id=identifier > 0x7FF,
            arbitration_id=identifier,
            data=data,
            is_remote_frame=False
        )
        with self.send_lock:
            msg.timestamp = time.time()
            try:
                self.bus.send(msg)
                logger.info(f"Message sent: {msg}")
            except can.CanError as e:
                logger.error(f"Error sending message: {e}")
        self.check()

    @abstractmethod
    def notify(self, identifier, data, timestamp):
        pass
    
    def check(self):
        if self.notifier:
            exc = self.notifier.exception
            if exc is not None:
                logger.error("An error has caused receiving of messages to stop")
                raise exc

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

class MessageListener(can.Listener):
    def __init__(self, bus):
        self.bus = bus

    def on_message_received(self, msg):
        if msg.is_error_frame or msg.is_remote_frame:
            return
        try:
            self.bus.notify(msg.arbitration_id, msg.data, msg.timestamp)
        except Exception as e:
            logger.error(str(e))