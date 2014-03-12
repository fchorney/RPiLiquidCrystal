#!/usr/bin/env python

import RPIO

from RPiLiquidCrystal import LCD

def main():
    # Rewrite pins for your own specification
    rs = 0
    enable = 1
    d4 = 2
    d5 = 3
    d6 = 4
    d7 = 5
    try:
        RPIO.setmode(RPIO.BCM)
        lcd = LCD(
            rs, enable, [d4, d5, d6, d7],
            lines=2, fourbitmode=True
        )
        lcd.clear()
        lcd.home()
        lcd.setCursor(0, 0)
        lcd.printMessage('Hello')
        lcd.setCursor(0, 1)
        lcd.printMessage('World')
    except KeyboardInterrupt:
        pass
    RPIO.cleanup()

if __name__ == '__main__':
    main()
