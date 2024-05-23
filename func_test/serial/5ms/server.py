import serial
import time
import threading

class SerialServer:
    def __init__(self, port='/dev/ttyAMA0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_port = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.004,  # 非阻塞模式
            write_timeout=0,  # 非阻塞模式
            xonxoff=False,  # 关闭软件流控制
            rtscts=False,  # 关闭硬件流控制
            dsrdtr=False  # 关闭硬件流控制
        )
        self.running = True

    def send_and_receive(self):
        last_time = time.time()
        while self.running:
            curr_time = time.time()
            try:
                # 发送字节
                self.serial_port.write(b'\x01\x02\x03')
                print('Sent: \x01\x02\x03')
                # 读取响应
                response = self.serial_port.read(3)
                if response == b'\x01\x02\x03':
                    print(f'Received: {response}, Response time: {time.time() - last_time:.6f} s')
                    last_time = time.time()
            except serial.SerialException as e:
                print(f'Serial error: {e}')
                self.running = False
            # 每次发送前等待 5 ms
            next_time = curr_time + 0.005
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def start(self):
        self.thread = threading.Thread(target=self.send_and_receive)
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join()
        self.serial_port.close()

if __name__ == '__main__':
    server = SerialServer()
    try:
        server.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()