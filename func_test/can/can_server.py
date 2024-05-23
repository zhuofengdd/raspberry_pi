from can_base import CanEcho
import time
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    filters = [
        {"can_id": 0x123, "can_mask": 0x7FF, "extended": False},
    ]
    can_obj = CanEcho()
    can_obj.connect_can('can0', filters=filters)
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt as e:
        logging.info(f"Interrupted: {e}")
    finally:
        can_obj.disconnect_can('can0')
        logging.info("CAN port closed")