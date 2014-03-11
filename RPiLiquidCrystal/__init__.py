import RPIO
import time

def delayMicroseconds(microseconds):
    seconds = float(microseconds) * 0.000001
    time.sleep(seconds)

class LCD:
    # Commands
    CLEARDISPLAY        = 0x01
    RETURNHOME          = 0x02
    ENTRYMODESET        = 0x04
    DISPLAYCONTROL      = 0x08
    CURSORSHIFT         = 0x10
    FUNCTIONSET         = 0x20
    SETCGRAMADDR        = 0x40
    SETDDRAMADDR        = 0x80

    # Flags for display entry mode
    ENTRYRIGHT          = 0x00
    ENTRYLEFT           = 0x02
    ENTRYSHIFTINCREMENT = 0x01
    ENTRYSHIFTDECREMENT = 0x00

    # Flags for display on/off control
    DISPLAYON           = 0x04
    DISPLAYOFF          = 0x00
    CURSORON            = 0x02
    CURSOROFF           = 0x00
    BLINKON             = 0x01
    BLINKOFF            = 0x00

    # Flags for display/cursor shift
    DISPLAYMOVE         = 0x08
    CURSORMOVE          = 0x00
    MOVERIGHT           = 0x04
    MOVELEFT            = 0x00

    # Flags for function set
    EIGHTBITMODE        = 0x10
    FOURBITMODE         = 0x00
    TWOLINE             = 0x08
    ONELINE             = 0x00
    FIVEBYTENDOTS       = 0x04
    FIVEBYEIGHTDOTS     = 0x00

    def __init__(
        self, rs, enable,
        d0, d1, d2, d3,
        d4, d5, d6, d7,
        fourbitmode=False, rw=255, cols=16, lines=1, dotsize=0
    ):
        self._rs = rs
        self._rw = rw
        self._enable = enable

        self._data_pins = []
        self._data_pins[0] = d0
        self._data_pins[1] = d1
        self._data_pins[2] = d2
        self._data_pins[3] = d3
        self._data_pins[4] = d4
        self._data_pins[5] = d5
        self._data_pins[6] = d6
        self._data_pins[7] = d7

        RPIO.setup(self._rs, RPIO.OUT)
        # We can save 1 pin by not using RW. Indicate by passing 255 instead
        # of pin number
        if self._rw != 255:
            RPIO.setup(self._rw, RPIO.OUT)
        RPIO.setup(self._enable, RPIO.OUT)

        # Set display function
        self._display_function = (
            LCD.EIGHTBITMODE | LCD.ONELINE | LCD.FIVEBYEIGHTDOTS
        )
        if fourbitmode:
            self._display_function = (
                LCD.FOURBITMODE | LCD.ONELINE | LCD.FIVEBYEIGHTDOTS
            )

        self._begin(cols, lines, dotsize)

    def _begin(self, cols, lines, dotsize):
        if lines > 1:
            self._display_function |= LCD.TWOLINE
        self._numlines = lines

        # For some 1 line displays you can select a 10 pixel high font
        if dotsize != 0 and lines == 1:
            self._display_function |= LCD.FIVEBYTENDOTS

        # See page 45/46 for initialization specification
        # According to the datasheet, we need at least 40 ms after power rises
        # above 2.7V before sending commands. We'll wait 50ms to be safe
        delayMicroseconds(50000)

        # Now we pull RS, Enable and R/W low to begin commands
        RPIO.output(self._rs, RPIO.LOW)
        RPIO.output(self._enable, RPIO.LOW)
        if self._rw != 255:
            RPIO.output(self._rw, RPIO.LOW)

        # Put the LCD into 4 bit or 8 bit mode
        if not self._display_function & LCD.EIGHTBITMODE:
            # This is according to the hitachi HD44780 datasheet
            # figure 24, pg 46

            # We start in 8-bit mode, try to set 4 bit mode
            self._write4bits(0x03)
            delayMicroseconds(4500) # Wait min 4.1ms

            # Second try
            self._write4bits(0x03)
            delayMicroseconds(4500) # Wait min 4.1ms

            # Third go!
            self._write4bits(0x03)
            delayMicroseconds(150)

            # Finally, set to 8-bit interface
            self._write4bits(0x02)
        else:
            # This is according to the hitachi HD44780 datasheet
            # page 45 figure 23

            # Send function set command sequence
            self._command(LCD.FUNCTIONSET | self._display_function)
            delayMicroseconds(4500) # Wait min 4.1ms

            # Second try
            self._command(LCD.FUNCTIONSET | self._display_function)
            delayMicroseconds(150)

            # Third go
            self._command(LCD.FUNCTIONSET | self._display_function)

        # Finally set the number of lines, font size, etc
        self._command(LCD.FUNCTIONSET | self._display_function)

        # Turn the display on with no cursor or blinking by default
        self._display_control = LCD.DISPLAYON | LCD.CURSOROFF | LCD.BLINKOFF
        self.display()

        # Clear it off
        self.clear()

        # Initialize to default text direction (for romance languages)
        self._display_mode = LCD.ENTRYLEFT | LCD.ENTRYSHIFTDECREMENT
        # Set the entry mode
        self._command(LCD.ENTRYMODESET | self._display_mode)

    # High level commands, for the user
    def clear(self):
        # Clear the display, set cursor position to zero
        self._command(LCD.CLEARDISPLAY)
        # This command takes a long time
        delayMicroseconds(2000)

    def home(self):
        # Set cursor position to zero
        self._command(LCD.RETURNHOME)
        # This command takes a long time
        delayMicroseconds(2000)

    def setCursor(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self._numlines:
            # We count rows starting with 0
            row = self._numlines - 1

        self._command(LCD.SETDDRAMADDR | (col + row_offsets[row]))

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

    # Allows us to fill the first 8 CGRAM locations
    # with custom characters
    def createChar(self, location, charmap):
        location &= 0x07; # We only have 8 locations 0-7
        self._command(LCD.SETCGRAMADDR | (location << 3))
        for i in range(0, 8):
            self._write(charmap[i])

    def printMessage(self, msg):
        for ch in msg:
            self._write(ord(ch))

    # Mid level commands for sending data/cmds
    def _command(self, value):
        self._send(value, RPIO.LOW)

    def _write(self, value):
        self._send(value, RPIO.HIGH)

    # Low level data pushing commands

    # Write either command or data, with automatic 4/8-bit selection
    def _send(self, value, mode):
        RPIO.output(self._rs, mode)

        # If there is an RW pin indicated, set it to low to Write
        if self._rw != 255:
            RPIO.output(self._rw, RPIO.LOW)

        if self._display_function & LCD.EIGHTBITMODE:
            self._write8bits(value)
        else:
            self._write4bits(value>>4)
            self._write4bits(value)

    def _pulseEnable(self):
        RPIO.output(self._enable, RPIO.LOW)
        delayMicroseconds(1)
        RPIO.output(self._enable, RPIO.HIGH)
        delayMicroseconds(1) # Enable pulse must be > 450ns
        RPIO.output(self._enable, RPIO.LOW)
        delayMicroseconds(100) # Commands need > 37us to settle

    def _write4bits(self, value):
        for i in range(0, 4):
            RPIO.setup(self._data_pins[i], RPIO.OUT)
            RPIO.output(self._data_pins[i], (value >> i) & 0x01)
        self._pulseEnable()

    def _write8bits(self, value):
        for i in range(0, 8):
            RPIO.setup(self._data_pins[i], RPIO.OUT)
            RPIO.output(self._data_pins[i], (value >> i) & 0x01)
        self._pulseEnable()
