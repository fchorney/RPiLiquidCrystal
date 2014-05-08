from Utils import delay_microseconds

class HD44780:
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


    # Write Modes
    WRITE_MODE_CMD          = 0x00
    WRITE_MODE_CHAR         = 0x01


    def __init__(self, protocol):
        # Keep Protocol
        self.protocol = protocol

        # Initialize
        self.__initialize()

        # Set Display Function
        self.__display_function = (
            HD44780.BIT_MODE_4 | HD44780.LINE_1 | HD44780.DOTS_5_BY_8
        )

        self.__begin()


    # Internal Protocol Functions
    def __initialize(self):
        self.protocol.initialize()


    def __send(self, value, mode):
        self.protocol.send(value, mode)


    def __write4bits(self, value):
        self.protocol.write4bits(value)


    # External Protocol Functions
    def enableBacklight(self, intensity=100):
        self.protocol.enableBacklight(intensity)


    def disableBacklight(self):
        self.protocol.disableBacklight()


    def cleanup(self):
        self.protocol.cleanup()


    def clear(self):
        # Clear the display, set the cursor position to zero
        self.__command(HD44780.CLEAR_DISPLAY)
        # This command takes a long time
        delay_microseconds(2000)


    def home(self):
        # Set cursor position to zero
        self.__command(HD44780.RETURN_HOME)
        # This command takes a long time
        delay_microseconds(2000)


    def setCursor(self, row, col):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self.protocol.numlines:
            # We count rows starting with 0
            row = self.protocol.numlines - 1

        self.__command(HD44780.SET_DDRAM_ADDR | (col + row_offsets[row]))


    def writeRaw(self, location, row, col):
        self.setCursor(row, col)
        self.__write(location)


    def write(self, msg, justify=JUSTIFY_LEFT):
        if justify == HD44780.JUSTIFY_RIGHT:
            msg = msg.rjust(self.protocol.columns)
        elif justify == HD44780.JUSTIFY_CENTER:
            msg = msg.center(self.protocol.columns)
        else:
            msg = msg.ljust(self.protocol.columns)

        for ch in msg:
            self.__write(ord(ch))


    # Allows us to fill the first 8 CGRAM locations
    # with custom characters
    def createChar(self, location, charmap):
        location &= 0x07
        self.__command(HD44780.SET_CGRAM_ADDR | (location << 3))
        for i in range(0, 8):
            self.__write(charmap[i])


    def __begin(self):
        # Assume two lines is lines is not 1
        if self.protocol.numlines > 1:
            self.__display_function |= HD44780.LINE_2

        # For some 1 line displays, you can select a 10 pixel high font
        # If dotsize is not 0, assume 5x10 pixel size
        if self.protocol.dotsize != 0 and self.protocol.numlines == 1:
            self.__display_function |= HD44780.DOTS_5_BY_10

        # According to the datasheet, we need at least 40 ms after power rises
        # above 2.7v before sending commands. We'll wait 50ms to be sage
        delay_microseconds(50000)

        # Call the protocols begin function here
        self.protocol.begin()

        # Put the LCD into 4 bit mode
        # This is according to the hitachi HD44780 datasheet
        # figure 24, pg 46

        # We start in 8-bit mode, try to set 4 bit mode
        self.__write4bits(0x03)
        delay_microseconds(4500)

        # Second try
        self.__write4bits(0x03)
        delay_microseconds(4500)

        # Third go
        self.__write4bits(0x03)
        delay_microseconds(150)

        # Finally, set to 4-bit interface
        self.__write4bits(0x02)

        # Finally set the number of lines, font size, etc
        self.__command(HD44780.FUNCTION_SET | self.__display_function)

        # Turn the display on with no cursor or blinking by default
        self.__display_control = (
            HD44780.DISPLAY_ON | HD44780.CURSOR_OFF | HD44780.BLINK_OFF
        )
        self.display()

        # Clear it off
        self.clear()

        # Initialize to default text direction (for romance languages)
        self.__display_mode = (
            HD44780.ENTRY_LEFT | HD44780.ENTRY_SHIFT_DECREMENT
        )

        # Set the entry mode
        self.__command(HD44780.ENTRY_MODE_SET | self.__display_mode)


    def __command(self, value):
        self.__send(value, HD44780.WRITE_MODE_CMD)


    def __write(self, value):
        self.__send(value, HD44780.WRITE_MODE_CHAR)


    # Turn the display on/off (quickly)
    def noDisplay(self):
        self.__display_control &= ~HD44780.DISPLAY_ON
        self.__command(HD44780.DISPLAY_CONTROL | self.__display_control)


    def display(self):
        self.__display_control |= HD44780.DISPLAY_ON
        self.__command(HD44780.DISPLAY_CONTROL | self.__display_control)


    # Turns the underline cursor on/off
    def noCursor(self):
        self.__display_control &= ~HD44780.CURSOR_ON
        self.__command(HD44780.DISPLAY_CONTROL | self.__display_control)


    def cursor(self):
        self.__display_control |= HD44780.CURSOR_ON
        self.__command(HD44780.DISPLAY_CONTROL | self.__display_control)


    # These commands scroll the display without changing the RAM
    def scrollDisplayLeft(self):
        self.__command(
            HD44780.CURSOR_SHIFT | HD44780.DISPLAY_MOVE | HD44780.MOVE_LEFT
        )


    def scrollDisplayRight(self):
        self.__command(
            HD44780.CURSOR_SHIFT | HD44780.DISPLAY_MOVE | HD44780.MOVE_RIGHT
        )


    # This is for text that flows Left to Right
    def leftToRight(self):
        self.__display_mode |= HD44780.ENTRY_LEFT;
        self.__command(HD44780.ENTRY_MODE_SET | self.__display_mode)


    # This is for text that flows Right to Left
    def rightToLeft(self):
        self.__display_mode &= ~HD44780.ENTRY_LEFT;
        self.__command(HD44780.ENTRY_MODE_SET | self.__display_mode)


    # This will 'right justify' text from the cursor
    def autoscroll(self):
        self.__display_mode |= HD44780.ENTRY_SHIFT_INCREMENT
        self.__command(HD44780.ENTRY_MODE_SET | self.__display_mode)


    # This will 'left justify' text from the cursor
    def noAutoscroll(self):
        self.__display_mode &= ~HD44780.ENTRY_SHIFT_INCREMENT
        self.__command(HD44780.ENTRY_MODE_SET | self.__display_mode)
