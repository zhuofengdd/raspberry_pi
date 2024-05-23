import canopen
import os
import logging
import time
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CanOpenMaster:
    def __init__(self):
        self.network = canopen.Network()
        self.running = False

    def connect_can(self, channel, bitrate=500000):
        try:
            os.system(f'sudo ip link set {channel} down')
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

    def heartbeat_callback(self,node_status):
        logger.info(f"Heartbeat received {node_status}")

    def add_slave(self, node_id, eds_file):
        try:
            node = canopen.RemoteNode(node_id, eds_file)
            self.network.add_node(node)
            node.nmt.send_command(0x81) #reset
            node.nmt.state = 'PRE-OPERATIONAL'
            node.nmt.wait_for_heartbeat(10)
            time.sleep(1)

            node.tpdo.read()
            node.rpdo.read()

            node.tpdo[1].clear()
            node.tpdo[1].add_variable('Statusword')
            node.tpdo[1].add_variable('Velocity actual value')
            node.tpdo[1].trans_type = 0xff
            node.tpdo[1].event_timer = 100
            node.tpdo[1].enabled = True
            node.tpdo[1].save()

            node.rpdo[1].clear()
            node.rpdo[1].add_variable(0x6077, 0)
            node.rpdo[1].add_variable(0x6078, 0)
            node.rpdo[1].add_variable(0x6079, 0)
            node.rpdo[1].enabled = True
            
            node.rpdo[1].save()
            node.rpdo[1].start(2)

            node.sdo[0x1005].raw = 0x00000080
            node.sdo[0x1006].raw = 1000
            self.network.sync.start(1)
            node.nmt.state = 'OPERATIONAL'

            node.nmt.add_hearbeat_callback(lambda _: self.heartbeat_callback(node_id))
            node.sdo['Producer Heartbeat Time'].raw = 2000 #can change heartbeat period 
            logger.info(f"Added slave node with ID {node_id} and set to OPERATIONAL")

            print('\r\n↓↓↓↓↓↓↓↓↓↓↓↓OD DISPLAY↓↓↓↓↓↓↓↓↓↓↓↓')
            for obj in node.object_dictionary.values():
                print('0x%X: %s' % (obj.index, obj.name))
                if isinstance(obj, canopen.objectdictionary.ODRecord):
                    for subobj in obj.values():
                        print('  %d: %s' % (subobj.subindex, subobj.name))
            self.network.subscribe(0x181, self.pdo_callback)
        except Exception as e:
            logger.error(f"Error adding slave node: {e}")

    def read_sdo_normal(self, node_id, index, subindex):
        try:
            value = self.network[node_id].sdo[index][subindex].raw
            logger.info(f"SDO {hex(index)}/{subindex} value: {value}")
            return value
        except Exception as e:
            logger.error(f"Error reading SDO {hex(index)}/{subindex}: {e}")
            return None

    def write_sdo_normal(self, node_id, index, subindex, value):
        try:
            self.network[node_id].sdo[index][subindex].raw = value
            logger.info(f"SDO {hex(index)}/{subindex} written with value: {value}")
        except Exception as e:
            logger.error(f"Error writing SDO {hex(index)}/{subindex}: {e}")

    def start_periodic_tasks(self, node_id, interval):
        def perform_tasks():
            while self.running:
                try:
                    # Read and write 4-byte SDO
                    sdo_value = self.read_sdo_normal(node_id, 0x2341, 2)
                    if sdo_value is not None:
                        new_sdo_value = sdo_value + 1
                        self.write_sdo_normal(node_id, 0x2341, 2, new_sdo_value)
                    # Read write string,can operate any len
                    sdo_value = self.read_sdo_normal(node_id, 0x2ff4,4)
                    if sdo_value is not None:
                        new_sdo_value = "AABBCCDDEEFFGGHH"
                        self.write_sdo_normal(node_id, 0x2FF4, 4, new_sdo_value)
                    self.network[node_id].sdo[0x6041].raw = self.network[node_id].sdo[0x6041].raw +1

                    self.network[node_id].rpdo[1][0x6077].raw = 1000
                    self.network[node_id].rpdo[1][0x6078].raw = 1
                    self.network[node_id].rpdo[1][0x6079].raw = 1000000
                    pass
                except Exception as e:
                    logger.error(f"Error in periodic tasks: {e}")

                time.sleep(interval)

        self.running = True
        thread = Thread(target=perform_tasks)
        thread.start()

    def pdo_callback(self,can_id, data, timestamp):
        logger.info(f"{hex(can_id)},{data}")