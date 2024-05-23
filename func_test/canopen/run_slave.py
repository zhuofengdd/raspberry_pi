from canopen_example.canopen_slave import CanOpenSlave
import time
import os
import logging

if __name__ == '__main__':
    slave = CanOpenSlave()
    slave.connect_can('can1')  # 确保连接到 'can1' 的从站
    eds_file_path = 'eds_files/example.eds'  # 提供 EDS 文件的正确路径

    if os.path.exists(eds_file_path):
        slave.initialize_slave(1, eds_file_path)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            slave.disconnect_can('can1')
    else:
        logger.error(f"EDS 文件 {eds_file_path} 不存在")