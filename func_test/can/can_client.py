import os
import can
import logging

logging.basicConfig(level=logging.INFO)

def setup_can_interface(channel, bitrate=500000):
    os.system(f'sudo ip link set {channel} type can bitrate {bitrate}')
    os.system(f'sudo ifconfig {channel} up')

def teardown_can_interface(channel):
    os.system(f'sudo ifconfig {channel} down')

def send_can_message(channel, identifier, data):
    try:
        can_bus = can.interface.Bus(channel=channel, bustype='socketcan')
        msg = can.Message(is_extended_id=False, arbitration_id=identifier, data=data)
        can_bus.send(msg)
        logging.info(f"Message sent: {msg}")
    except can.CanError as e:
        logging.error(f"Error sending CAN message: {e}")
    finally:
        can_bus.shutdown()

if __name__ == "__main__":
    setup_can_interface('can1')
    send_can_message('can1', 0x123, [0, 1, 2, 3, 4, 5, 6, 7])
    teardown_can_interface('can1')