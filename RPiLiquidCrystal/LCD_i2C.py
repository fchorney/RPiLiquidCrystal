import smbus

from HD44780 import HD44780
from Utils import delay_microseconds


class i2c_device:
    def __init__(self, addr=0x27, port=1):
        self.addr = addr
        self.port = port
        self.bus = smbus.SMBus(port)


    # Write a single command
    def write_cmd(self, cmd):
        self.bus.write_byte(self.addr, cmd)
        delay_microseconds(100)


    # Write a command and argument
    def write_cmd_arg(self, cmd, data):
        self.bus.write_byte_data(self.addr, cmd, data)
        delay_microseconds(100)


    # Write a block of data
    def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        delay_microseconds(100)


    # Read a single byte
    def read(self):
        return self.bus.read_byte(self.addr)


    # Read
    def read_data(self, cmd):
        return self.bus.read_byte_data(self.addr, cmd)


    # Read a block of data
    def read_block_data(self, cmd):
        return self.bus.read_block_data(self.addr, cmd)


    # Clean up
    def cleanup(self):
        self.bus.close()


class LCD_Protocol():
    # Backlight Settings
    BACKLIGHT               = 0x08


    # Special Bits
    ENABLE_BIT              = 0b00000100


    def __init__(self, i2c_addr, cols=16, lines=1, dotsize=0):
        # Internal Variables
        self.__i2c_addr = i2c_addr
        self.__i2c_bus = None

        # Public Variables
        self.numlines = lines
        self.columns = cols
        self.dotsize = dotsize


    # Protocol Functions
    def initialize(self):
        self.__i2c_bus = i2c_device(self.__i2c_addr)


    def begin(self):
        pass

    def send(self, value, mode):
        self.write4bits(mode | (value & 0xF0))
        self.write4bits(mode | ((value << 4) & 0xF0))


    def write4bits(self, value):
        self.__i2c_bus.write_cmd(value | LCD_Protocol.BACKLIGHT)
        self.__pulse_enable(value)


    # XXX: Figure out how to control the backlight through i2C code
    def enableBacklight(self, intensity=100):
        pass


    def disableBacklight(self):
        pass


    def cleanup(self):
        self.__i2c_bus.cleanup()


    # Internal Functions
    def __pulse_enable(self, data):
        self.__i2c_bus.write_cmd(
            data | LCD_Protocol.ENABLE_BIT | LCD_Protocol.BACKLIGHT
        )
        delay_microseconds(5)
        self.__i2c_bus.write_cmd(
            ((data & ~ LCD_Protocol.ENABLE_BIT) | LCD_Protocol.BACKLIGHT))
        delay_microseconds(5)


def LCD(i2c_addr, cols=16, lines=1, dotsize=0):
    return HD44780(LCD_Protocol(i2c_addr, cols, lines, dotsize))
