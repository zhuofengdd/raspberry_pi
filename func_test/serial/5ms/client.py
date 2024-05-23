import serial
import time
import threading

class SerialClient:
    def __init__(self, port='/dev/ttyAMA1', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_port = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0,  # 非阻塞模式
            write_timeout=0,  # 非阻塞模式
            xonxoff=False,  # 关闭软件流控制
            rtscts=False,  # 关闭硬件流控制
            dsrdtr=False  # 关闭硬件流控制
        )
        self.running = True

    def receive_and_respond(self):
        data = bytearray(3)
        last_time = time.time()
        while self.running:
            try:
                # 读取传入的数据
                incoming_data = self.serial_port.read(3)
                if incoming_data:
                    data[:] = incoming_data
                    if data == b'\x01\x02\x03':
                        print(f'Received: {data}')
                        self.serial_port.write(data)  # 回显接收到的数据
                        print(f'Response time: {time.time() - last_time:.6f} s')
                        last_time = time.time()
            except serial.SerialException as e:
                print(f'Serial error: {e}')
                self.running = False
            time.sleep(0.001)  # 确保 CPU 不会被完全占用
    
    def start(self):
        self.thread = threading.Thread(target=self.receive_and_respond)
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join()
        self.serial_port.close()

if __name__ == '__main__':
    client = SerialClient()
    try:
        client.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.stop()