from .can_base_class import CanBaseClass
import os
import logging

logger = logging.getLogger(__name__)

class CanEcho(CanBaseClass):
    def __init__(self):
        super().__init__()
    
    def connect_can(self, channel, bitrate=500000, filters=None):
        try:
            os.system(f'sudo ip link set {channel} type can bitrate {bitrate}')
            os.system(f'sudo ifconfig {channel} up')
            self.connect(channel=channel, bustype='socketcan', can_filters=filters)
            logger.info(f"CAN interface {channel} brought up with bitrate {bitrate}")
        except Exception as e:
            logger.error(f"Error setting up CAN interface {channel}: {e}")
            raise

    def disconnect_can(self, channel):
        try:
            self.disconnect()
            os.system(f'sudo ifconfig {channel} down')
            logger.info(f"CAN interface {channel} brought down")
        except Exception as e:
            logger.error(f"Error tearing down CAN interface {channel}: {e}")

    def notify(self, identifier, data, timestamp):
        logger.info(f'Received message: identifier={hex(identifier)}, data={data}')
        try:
            self.send_message(identifier, data)
        except Exception as e:
            logger.error(f"Error echoing message: {e}")