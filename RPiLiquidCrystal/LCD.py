import time
import RPIO as GPIO
import RPIO.PWM as PWM

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


    def __init__(
        self, rs, enable, pins,
        backlight=None, rw=None,
        cols=16, lines=1, dotsize=0
    ):
        self._rs = rs
        self._rw = rw
        self._enable = enable
        self._data_pins = pins
        self._numlines = lines
        self._columns = cols
        self._dotsize = dotsize
        self._backlight = backlight

        # Setup PWM is backlight is defined
        if self._backlight:
            PWM.setup()
            PWM.init_channel(0)
            self.enableBacklight()

        # Setup rs, enable and rw pins
        GPIO.setup(self._rs, GPIO.OUT)
        GPIO.setup(self._enable, GPIO.OUT)
        if self._rw:
            GPIO.setup(self._rw, GPIO.OUT)

        # Set Display Function
        self._display_function = (
            LCD.BIT_MODE_4 | LCD.LINE_1 | LCD.DOTS_5_BY_8
        )
        if len(pins) == 8:
            self._display_function = (
                LCD.BIT_MODE_8 | LCD.LINE_1 | LCD.DOTS_5_BY_8
            )

        self.__begin()


    def cleanup(self):
        if self._backlight:
            PWM.clear_channel_gpio(0, self._backlight)
            PWM.cleanup()
        GPIO.cleanup()

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


    def write(self, msg, justify=JUSTIFY_LEFT):
        if justify == LCD.JUSTIFY_RIGHT:
            msg = msg.rjust(self.columns)
        elif justify == LCD.JUSTIFY_CENTER:
            msg = msg.center(self.columns)
        else:
            msg = msg.ljust(self.columns)

        for ch in msg:
            self.__write(ord(ch))


    # Allows us to fill the first 8 CGRAM locations
    # with custom characters
    def createChar(self, location, charmap):
        location &= 0x07
        self.__command(LCD.SET_CGRAM_ADDR | (location << 3))
        for i in range(0, 8):
            self.__write(charmap([i]))


    def __begin(self):
        # Assume two lines is lines is not 1
        if self._numlines > 1:
            self._display_function |= LCD.LINE_2

        # For some 1 line displays, you can select a 10 pixel high font
        # If dotsize is not 0, assume 5x10 pixel size
        if self.dotsize != 0 and self.numlines == 1:
            self._display_function |= LCD.DOTS_5_BY_10

        # According to the datasheet, we need at least 40 ms after power rises
        # above 2.7v before sending commands. We'll wait 50ms to be sage
        self.__delay_microseconds(50000)

        # Now we pull RS, Enable and R/W low to begin commands
        GPIO.output(self._rs, GPIO.LOW)
        GPIO.output(self._enable, GPIO.LOW)
        if self._rw:
            GPIO.output(self._rw, GPIO.LOW)

        # Put the LCD into 4 bit or 8 bit mode
        if not self.display_function & LCD.BIT_MODE_8:
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
        self.__send(value, GPIO.LOW)


    def __write(self, value):
        self.__send(value, GPIO.HIGH)


    def __send(self, value, mode):
        GPIO.output(self._rs, mode)

        # If there is an RW pin incicated, set it to low to write
        if self._rw:
            GPIO.output(self._rw, GPIO.LOW)

        if self._display_function & LCD.BIT_MODE_8:
            self.__write8bits(value)
        else:
            self.__write4bits(value>>4)
            self.__write4bits(value)


    def __write_bits(self, value, numberofbits=8):
        for i in range(0, numberofbits):
            GPIO.setup(self._data_pins[i], GPIO.OUT)
            GPIO.output(self._data_pins[i], (value >> i) & 0x01)
        self.__pulse_enable()


    def __write8bits(self, value):
        self.__write_bits(value)


    def __write4bits(self, value):
        self.__write_bits(value, numberofbits=4)


    def __pulse_enable(self):
        GPIO.output(self._enable, GPIO.LOW)
        self.__delay_microseconds(1)
        GPIO.output(self._enable, GPIO.HIGH)
        self.__delay_microseconds(1)
        GPIO.output(self._enable, GPIO.LOW)
        self.__delay_microseconds(100)


    def enableBacklight(self, intensity=10):
        # If no backlight pin is assigned, just return
        if not self.backlight:
            return

        # Clamp our intensity to be between 0 and 10
        if intensity > 10:
            intensity = 10
        if intensity < 0:
            intensity = 0

        # Set PWM
        PWM.add_channel_pulse(0, self._backlight, 0, (intensity * 10))

    def disableBacklight(self):
        self.enableBacklight(intensity=0)

    # Turn the display on/off (quickly)
    def noDisplay(self):
        self._display_control &= ~LCD.DISPLAYON
        self._command(LCD.DISPLAYCONTROL | self._display_control)


    def display(self):
        self._display_control |= LCD.DISPLAYON
        self._command(LCD.DISPLAYCONTROL | self._display_control)


    # Turns the underline cursor on/off
    def noCursor(self):
        self._display_control &= ~LCD.CURSORON
        self._command(LCD.DISPLAYCONTROL | self._display_control)


    def cursor(self):
        self._display_control |= LCD.CURSORON
        self._command(LCD.DISPLAYCONTROL | self._display_control)


    # These commands scroll the display without changing the RAM
    def scrollDisplayLeft(self):
        self._command(LCD.CURSORSHIFT | LCD.DISPLAYMOVE | LCD.MOVELEFT)


    def scrollDisplayRight(self):
        self._command(LCD.CURSORSHIFT | LCD.DISPLAYMOVE | LCD.MOVERIGHT)


    # This is for text that flows Left to Right
    def leftToRight(self):
        self._display_mode |= LCD.ENTRYLEFT;
        self._command(LCD.ENTRYMODESET | self._display_mode)


    # This is for text that flows Right to Left
    def rightToLeft(self):
        self._display_mode &= ~LCD.ENTRYLEFT;
        self._command(LCD.ENTRYMODESET | self._display_mode)


    # This will 'right justify' text from the cursor
    def autoscroll(self):
        self._display_mode |= LCD.ENTRYSHIFTINCREMENT
        self._command(LCD.ENTRYMODESET | self._display_mode)


    # This will 'left justify' text from the cursor
    def noAutoscroll(self):
        self._display_mode &= ~LCD.ENTRYSHIFTINCREMENT
        self._command(LCD.ENTRYMODESET | self._display_mode)


