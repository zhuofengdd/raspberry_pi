import serial
import time

uart = serial.Serial(port="/dev/ttyAMA0",baudrate=115200, timeout=0.5, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)

# send 50 times
try:
    while 1:
        if uart.in_waiting > 0:
            # 读取数据
            data = uart.read(uart.in_waiting)
            print(f"Received: {data}")
            
            # 回显数据
            uart.write(data)
            print(f"Echoed: {data}") 

except serial.SerialException as e:
    print(f"Error opening or using serial port: {e}")
finally:
    # 关闭串口
    if uart.is_open:
        uart.close()
        print("Closed serial port")    
