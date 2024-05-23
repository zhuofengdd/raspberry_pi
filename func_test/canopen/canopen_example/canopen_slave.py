import can
import canopen
import os
import logging
import time
from threading import Thread
from canopen.objectdictionary import ODVariable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CanOpenSlave:
    def __init__(self):
        self.network = canopen.Network()
        self.node = None
        self.running = False

    def connect_can(self, channel, bitrate=500000):
        try:
            os.system(f'sudo ip link set {channel} type can bitrate {bitrate}')
            os.system(f'sudo ifconfig {channel} up')
            self.network.connect(channel=channel, bustype='socketcan')
            logger.info(f"CAN interface {channel} brought up with bitrate {bitrate}")
        except Exception as e:
            logger.error(f"Error setting up CAN interface {channel}: {e}")
            raise

    def disconnect_can(self, channel):
        try:
            self.running = False
            self.network.disconnect()
            os.system(f'sudo ifconfig {channel} down')
            logger.info(f"CAN interface {channel} brought down")
        except Exception as e:
            logger.error(f"Error tearing down CAN interface {channel}: {e}")

    def initialize_slave(self, node_id, eds_file):
        try:
            self.node = canopen.LocalNode(node_id, eds_file)
            self.node = self.network.create_node(self.node)
            self.node.nmt.send_command(0) # bootup
            self.node.nmt.state = 'PRE-OPERATIONAL'
            self.node.nmt.start_heartbeat(1000)
            self.node.add_read_callback(self.some_read_callback)
            self.node.add_write_callback(self.some_write_callback)
            self.network.subscribe(0x220, self.pdo_callback)
            self.network.send_periodic(0x181, b'\x01\x20\x02\x00\x01\x02\x03\x04',2)
            logger.info(f"Initialized slave node with ID {node_id} in PRE-OPERATIONAL state")
        except Exception as e:
            logger.error(f"Error initializing slave node: {e}")

    def some_read_callback(self, **kwargs):
        logger.info(f"read cb:{hex(kwargs['index'])},{kwargs['subindex']}")

    def some_write_callback(self, **kwargs):
        logger.info(f"write cb:{hex(kwargs['index'])},{kwargs['subindex']},{kwargs['data']}")

    def pdo_callback(self,can_id, data, timestamp):
        logger.info(f"{hex(can_id)},{data}")