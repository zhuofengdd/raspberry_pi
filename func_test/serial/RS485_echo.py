import serial
import serial.rs485

def serial_echo(port, baudrate):
    try:
        # 打开RS485串口
        ser = serial.rs485.RS485(port, baudrate, timeout=1)
        
        # 配置RS485模式，手动控制RTS引脚
        ser.rs485_mode = serial.rs485.RS485Settings(
            rts_level_for_tx=True,  # 发送时RTS引脚为高电平
            rts_level_for_rx=False, # 接收时RTS引脚为低电平
            delay_before_tx=None,   # 发送前的延迟
            delay_before_rx=0.01    # 接收前的延迟
        )

        print(f"Opened RS485 port {port} with baudrate {baudrate}")

        while True:
            if ser.in_waiting > 0:
                # 读取数据
                data = ser.read(ser.in_waiting)
                print(f"Received: {data}")
                
                # 回显数据
                ser.write(data)
                print(f"Echoed: {data}")

    except serial.SerialException as e:
        print(f"Error opening or using serial port: {e}")

    finally:
        # 关闭串口
        if ser.is_open:
            ser.close()
            print("Closed serial port")

if __name__ == "__main__":
    # 修改为你的USB串口设备
    serial_port = "/dev/ttyUSB0"  # USB串口设备
    baud_rate = 115200  # 设置波特率
    serial_echo(serial_port, baud_rate)