import spidev
import time

# 初始化SPI
spi0 = spidev.SpiDev()

spi0.open(0, 0)  # 打开SPI0，设备0

spi0.max_speed_hz = 50000  # 设置SPI0的最大速度

# 设置SPI模式（0-3）
spi0.mode = 0  # SPI模式0

def send_and_receive_spi0(data):
    response = spi0.xfer2(data)
    return response

try:
    while True:
        send_data = [0x01, 0x02, 0x03, 0x04, 0x05]  # 发送的数据
        print(f'Sent: {send_data}')
        received_data = send_and_receive_spi0(send_data)  # 发送并接收数据
        print(f'Received: {received_data}')
        time.sleep(1)  # 延时1秒
except KeyboardInterrupt:
    spi0.close()