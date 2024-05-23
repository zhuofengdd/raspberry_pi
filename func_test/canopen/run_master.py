from canopen_example.canopen_master import CanOpenMaster
import time

if __name__ == '__main__':
    master = CanOpenMaster()
    master.connect_can('can0')
    master.add_slave(1, 'eds_files/example.eds')
    master.start_periodic_tasks(1, 2)  # Perform tasks every 2 seconds

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        master.disconnect_can('can0')