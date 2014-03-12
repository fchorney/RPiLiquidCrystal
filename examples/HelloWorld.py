#!/usr/bin/env python

import RPIO
import time
from RPiLiquidCrystal import LCD

PIN = {
    'GPIO0':   3,
    'GPIO1':   5,
    'GPIO4':   7,
    'GPIO7':  26,
    'GPIO8':  24,
    'GPIO9':  21,
    'GPIO10': 19,
    'GPIO11': 23,
    'GPIO14':  8,
    'GPIO15': 10,
    'GPIO17': 11,
    'GPIO18': 12,
    'GPIO21': 13,
    'GPIO22': 15,
    'GPIO23': 16,
    'GPIO24': 18,
    'GPIO25': 22,
}

def main():
    # Rewrite pins for your own specification
    RS      = PIN['GPIO23']
    ENABLE  = PIN['GPIO24']
    D4      = PIN['GPIO17']
    D5      = PIN['GPIO4']
    D6      = PIN['GPIO22']
    D7      = PIN['GPIO18']
    try:
        RPIO.setmode(RPIO.BOARD)
        lcd = LCD(
            RS, ENABLE, [D4, D5, D6, D7],
            lines=2, fourbitmode=True
        )
        lcd.setCursor(0, 0)
        lcd.printMessage('Hello')
        lcd.setCursor(0, 1)
        lcd.printMessage('World')
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    RPIO.cleanup()

if __name__ == '__main__':
    main()
