import RPi.GPIO as GPIO
import time
import logging

class RaspberryPiGPIO:
    def __init__(self, pin, mode=GPIO.BOARD, frequency=50, direction=GPIO.OUT):
        self.pin = pin
        self.frequency = frequency
        GPIO.setmode(mode)
        GPIO.setup(self.pin, direction)
        GPIO.setwarnings(False)
        self.pwm = None

        # Setup logger
        self.logger = logging.getLogger('RaspberryPiGPIO')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        self.logger.info(f'GPIO {self.pin} initialized as {"OUTPUT" if direction == GPIO.OUT else "INPUT"}.')

    def blink(self, times=50, interval=1):
        for i in range(times):
            GPIO.output(self.pin, GPIO.HIGH)
            self.logger.info(f'{self.pin} HIGH')
            time.sleep(interval)

            GPIO.output(self.pin, GPIO.LOW)
            self.logger.info(f'{self.pin} LOW')
            time.sleep(interval)

        self.cleanup()

    def start_pwm(self):
        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(0)
        self.logger.info(f'PWM started on pin {self.pin} with frequency {self.frequency} Hz')

    def change_duty_cycle(self, duty_cycle):
        if self.pwm is not None:
            self.pwm.ChangeDutyCycle(duty_cycle)
            self.logger.info(f'Duty cycle changed to {duty_cycle}%')
        else:
            self.logger.error('PWM not started yet. Call start_pwm() first.')

    def sweep_pwm(self, interval=0.1):
        try:
            while True:
                for dc in range(0, 101, 5):
                    self.change_duty_cycle(dc)
                    time.sleep(interval)
                for dc in range(100, -1, -5):
                    self.change_duty_cycle(dc)
                    time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info('PWM sweep interrupted by user')
            pass
        self.stop_pwm()

    def stop_pwm(self):
        if self.pwm is not None:
            self.pwm.stop()
            self.logger.info('PWM stopped')
        else:
            self.logger.error('PWM not started yet. Call start_pwm() first.')
        self.cleanup()

    def read_level(self):
        level = GPIO.input(self.pin)
        self.logger.info(f'GPIO {self.pin} level read: {"HIGH" if level else "LOW"}')
        return level

    def cleanup(self):
        GPIO.cleanup()
        self.logger.info(f'GPIO {self.pin} cleaned up')


if __name__ == "__main__":
    # Blinking example
    gpio_blink = RaspberryPiGPIO(11)
    gpio_blink.blink(times=10, interval=0.5)

    # PWM example
    gpio_pwm = RaspberryPiGPIO(11)
    gpio_pwm.start_pwm()
    gpio_pwm.sweep_pwm(interval=0.05)

    # Input level reading example
    gpio_input = RaspberryPiGPIO(13, direction=GPIO.IN)
    try:
        while True:
            level = gpio_input.read_level()
            print(f'GPIO 13 level: {"HIGH" if level else "LOW"}')
            time.sleep(1)
    except KeyboardInterrupt:
        gpio_input.cleanup()