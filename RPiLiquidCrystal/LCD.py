import RPIO as GPIO
import RPIO.PWM as PWM

from HD44780 import HD44780
from Utils import delay_microseconds


class LCD_Protocol():
    def __init__(
            self, rs, enable, pins,
            backlight=None, rw=None,
            cols=16, lines=1, dotsize=0):
        # Interal Variables
        self.__rs = rs
        self.__rw = rw
        self.__enable = enable
        self.__data_pins = pins
        self.__backlight = backlight

        # Public Variables
        self.numlines = lines
        self.columns = cols
        self.dotsize = dotsize


    # Protocol Functions
    def initialize(self):
        # Setup PWM if backlight is defined
        if self.__backlight:
            PWM.setup()
            PWM.init_channel(0)
            self.enableBacklight()

        # Setup rs, enable and rw pins
        GPIO.setup(self.__rs, GPIO.OUT)
        GPIO.setup(self.__enable, GPIO.OUT)
        if self.__rw:
            GPIO.setup(self.__rw, GPIO.OUT)


    def begin(self):
        # Pull RS, Enable and R/W low to begin commands
        GPIO.output(self.__rs, GPIO.LOW)
        GPIO.output(self.__enable, GPIO.LOW)
        if self.__rw:
            GPIO.output(self.__rw, GPIO.LOW)


    def send(self, value, mode):
        GPIO.output(self.__rs, mode)

        # If there is an RW pin incicated, set it to low to write
        if self.__rw:
            GPIO.output(self.__rw, GPIO.LOW)

        # Write both nibbles
        self.write4bits(value>>4)
        self.write4bits(value)


    def write4bits(self, value):
        for i in range(0, 4):
            GPIO.setup(self.__data_pins[i], GPIO.OUT)
            GPIO.output(self.__data_pins[i], (value >> i) & 0x01)
        self.__pulse_enable()


    def enableBacklight(self, intensity=100):
        self.__setBrightness(intensity)


    def disableBacklight(self):
        self.__setBrightness(0)


    def cleanup(self):
        if self.__backlight:
            PWM.clear_channel_gpio(0, self.__backlight)
            PWM.cleanup()
        GPIO.cleanup()


    # Internal Functions
    def __setBrightness(self, intensity):
        # If no backlight pin is assigned, just return
        if not self.__backlight:
            return

        # Clamp our intensity to be between 0 and 100 percent
        if intensity > 100:
            intensity = 100
        if intensity < 0:
            intensity = 0

        # Maximum width is 1999 based on the 20000us subcycle
        width = int(1999.0 * (intensity / 100.0))

        # Set PWM
        PWM.add_channel_pulse(0, self.__backlight, 0, width)


    def __pulse_enable(self):
        GPIO.output(self.__enable, GPIO.LOW)
        delay_microseconds(1)
        GPIO.output(self.__enable, GPIO.HIGH)
        delay_microseconds(1)
        GPIO.output(self.__enable, GPIO.LOW)
        delay_microseconds(100)


def LCD(
    rs, enable, pins,
    backlight=None, rw=None,
    cols=16, lines=1, dotsize=0
):
    return HD44780(
        LCD_Protocol(
            rs, enable, pins, backlight, rw, cols, lines, dotsize
        )
    )
