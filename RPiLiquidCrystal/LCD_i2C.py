import time
import smbus


class i2c_device:
    def __init__(self, addr=0x27, port=1):
        self.addr = addr
        self.port = port
        self.bus = smbus.SMBus(port)

    # Write a single command
    def write_cmd(self, cmd):
        self.bus.write_byte(self.addr, cmd)
        time.sleep(0.0001)

    # Write a command and argument
    def write_cmd_arg(self, cmd, data):
        self.bus.write_byte_data(self.addr, cmd, data)
        time.sleep(0.0001)

    # Write a block of data
    def write_block_data(self, cmd, data):
        self.bus.write_block_data(self.addr, cmd, data)
        time.sleep(0.0001)

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


class LCD:
    # Commands
    CLEAR_DISPLAY           = 0x01
    RETURN_HOME             = 0x02
    ENTRY_MODE_SET          = 0x04
    DISPLAY_CONTROL         = 0x08
    CURSOR_SHIFT            = 0x10
    FUNCTION_SET            = 0x20
    SET_CGRAM_ADDR          = 0x40
    SET_DDRAM_ADDR          = 0x80


    # Flags for display entry mode
    ENTRY_RIGHT             = 0x00
    ENTRY_LEFT              = 0x02
    ENTRY_SHIFT_INCREMENT   = 0x01
    ENTRY_SHIFT_DECREMENT   = 0x00


    # Flags for display on/off control
    DISPLAY_ON              = 0x04
    DISPLAY_OFF             = 0x00
    CURSOR_ON               = 0x02
    CURSOR_OFF              = 0x00
    BLINK_ON                = 0x01
    BLINK_OFF               = 0x00


    # Flags for display/cursor shift
    DISPLAY_MOVE            = 0x08
    CURSOR_MOVE             = 0x00
    MOVE_RIGHT              = 0x04
    MOVE_LEFT               = 0x00


    # Flags for function set
    BIT_MODE_8              = 0x10
    BIT_MODE_4              = 0x00
    LINE_2                  = 0x08
    LINE_1                  = 0x00
    DOTS_5_BY_10            = 0x04
    DOTS_5_BY_8             = 0x00


    # Justification settings
    JUSTIFY_LEFT            = 0x00
    JUSTIFY_RIGHT           = 0x01
    JUSTIFY_CENTER          = 0x02


    # Backlight settings
    BACKLIGHT               = 0x08
    NOBACKLIGHT             = 0x00

    # Special Bits
    ENABLE_BIT              = 0b00000100
    READ_WRITE_BIT          = 0b00000010
    REGISTER_SELECT_BIT     = 0b00000001


    def __init__(self, i2c_addr, cols=16, lines=1, dotsize=0):
        self._i2c = i2c_device(i2c_addr)
        self._numlines = lines
        self._columns = cols
        self._dotsize = dotsize

        # Set Display Function
        self._display_function = (
            LCD.BIT_MODE_4 | LCD.LINE_1 | LCD.DOTS_5_BY_8
        )

        self.__begin()


    def cleanup(self):
        self._i2c.cleanup()


    def clear(self):
        # Clear the display, set the cursor position to zero
        self.__command(LCD.CLEAR_DISPLAY)
        # This command takes a long time
        self.__delay_microseconds(2000)


    def home(self):
        # Set cursor position to zero
        self.__command(LCD.RETURN_HOME)
        # This command takes a long time
        self.__delay_microseconds(2000)


    def setCursor(self, row, col):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self._numlines:
            # We count rows starting with 0
            row = self._numlines - 1

        self.__command(LCD.SET_DDRAM_ADDR | (col + row_offsets[row]))


    def writeRaw(self, location, row, col):
        self.setCursor(row, col)
        self.__write(location)


    def write(self, msg, justify=JUSTIFY_LEFT):
        if justify == LCD.JUSTIFY_RIGHT:
            msg = msg.rjust(self._columns)
        elif justify == LCD.JUSTIFY_CENTER:
            msg = msg.center(self._columns)
        else:
            msg = msg.ljust(self._columns)

        for ch in msg:
            self.__write(ord(ch))


    # Allows us to fill the first 8 CGRAM locations
    # with custom characters
    def createChar(self, location, charmap):
        location &= 0x07
        self.__command(LCD.SET_CGRAM_ADDR | (location << 3))
        for i in range(0, 8):
            self.__write(charmap[i])


    def __begin(self):
        # Assume two lines is lines is not 1
        if self._numlines > 1:
            self._display_function |= LCD.LINE_2

        # For some 1 line displays, you can select a 10 pixel high font
        # If dotsize is not 0, assume 5x10 pixel size
        if self._dotsize != 0 and self._numlines == 1:
            self._display_function |= LCD.DOTS_5_BY_10

        # According to the datasheet, we need at least 40 ms after power rises
        # above 2.7v before sending commands. We'll wait 50ms to be sage
        self.__delay_microseconds(50000)


        # Put the LCD into 4 bit or 8 bit mode
        if not self._display_function & LCD.BIT_MODE_8:
            # This is according to the hitachi HD44780 datasheet
            # figure 24, pg 46

            # We start in 8-bit mode, try to set 4 bit mode
            self.__write4bits(0x03)
            self.__delay_microseconds(4500)

            # Second try
            self.__write4bits(0x03)
            self.__delay_microseconds(4500)

            # Third go
            self.__write4bits(0x03)
            self.__delay_microseconds(150)

            # Finally, set to 8-bit interface
            self.__write4bits(0x02)
        else:
            # This is according to the hitachi HD44780 datasheet
            # figure 23, pg 45

            # Send function set command sequence
            self.__command(LCD.FUNCTION_SET | self._display_function)
            self.__delay_microseconds(4500)

            # Second try
            self.__command(LCD.FUNCTION_SET | self._display_function)
            self.__delay_microseconds(150)

            # Thrid go
            self.__command(LCD.FUNCTION_SET | self._display_function)

        # Finally set the number of lines, font size, etc
        self.__command(LCD.FUNCTION_SET | self._display_function)

        # Turn the display on with no cursor or blinking by default
        self._display_control = (
            LCD.DISPLAY_ON | LCD.CURSOR_OFF | LCD.BLINK_OFF
        )
        self.display()

        # Clear it off
        self.clear()

        # Initialize to default text direction (for romance languages)
        self._display_mode = LCD.ENTRY_LEFT | LCD.ENTRY_SHIFT_DECREMENT

        # Set the entry mode
        self.__command(LCD.ENTRY_MODE_SET | self._display_mode)


    def __delay_microseconds(self, microseconds):
        seconds = float(microseconds) * 0.000001
        time.sleep(seconds)


    def __command(self, value):
        self.__send(value, 0)


    def __write(self, value):
        self.__send(value, LCD.REGISTER_SELECT_BIT)


    def __send(self, value, mode=0):
        self.__write4bits(mode | (value & 0xF0))
        self.__write4bits(mode | ((value << 4) & 0xF0))


    def __write4bits(self, value):
        self._i2c.write_cmd(value | LCD.BACKLIGHT)
        self.__pulse_enable(value)


    def __pulse_enable(self, data):
        self._i2c.write_cmd(data | LCD.ENABLE_BIT | LCD.BACKLIGHT)
        self.__delay_microseconds(5)
        self._i2c.write_cmd(((data & ~ LCD.ENABLE_BIT) | LCD.BACKLIGHT))
        self.__delay_microseconds(5)


    # Turn the display on/off (quickly)
    def noDisplay(self):
        self._display_control &= ~LCD.DISPLAY_ON
        self.__command(LCD.DISPLAY_CONTROL | self._display_control)


    def display(self):
        self._display_control |= LCD.DISPLAY_ON
        self.__command(LCD.DISPLAY_CONTROL | self._display_control)


    # Turns the underline cursor on/off
    def noCursor(self):
        self._display_control &= ~LCD.CURSO_RON
        self.__command(LCD.DISPLAY_CONTROL | self._display_control)


    def cursor(self):
        self._display_control |= LCD.CURSOR_ON
        self.__command(LCD.DISPLAY_CONTROL | self._display_control)


    # These commands scroll the display without changing the RAM
    def scrollDisplayLeft(self):
        self.__command(LCD.CURSOR_SHIFT | LCD.DISPLAY_MOVE | LCD.MOVE_LEFT)


    def scrollDisplayRight(self):
        self.__command(LCD.CURSOR_SHIFT | LCD.DISPLAY_MOVE | LCD.MOVE_RIGHT)


    # This is for text that flows Left to Right
    def leftToRight(self):
        self._display_mode |= LCD.ENTRY_LEFT;
        self.__command(LCD.ENTRY_MODE_SET | self._display_mode)


    # This is for text that flows Right to Left
    def rightToLeft(self):
        self._display_mode &= ~LCD.ENTRY_LEFT;
        self.__command(LCD.ENTRY_MODE_SET | self._display_mode)


    # This will 'right justify' text from the cursor
    def autoscroll(self):
        self._display_mode |= LCD.ENTRY_SHIFT_INCREMENT
        self.__command(LCD.ENTRY_MODE_SET | self._display_mode)


    # This will 'left justify' text from the cursor
    def noAutoscroll(self):
        self._display_mode &= ~LCD.ENTRY_SHIFT_INCREMENT
        self.__command(LCD.ENTRY_MODE_SET | self._display_mode)


