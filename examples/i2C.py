#!/usr/bin/env python

import time
from RPiLiquidCrystal.HD44780 import HD44780
from RPiLiquidCrystal.LCD_i2C import LCD


def main():
    CUSTOM_CHARS = {
        0: [
            0b00000,
            0b10001,
            0b10001,
            0b10001,
            0b00000,
            0b10001,
            0b01110,
            0b00000
        ],
        1: [
            0b00000,
            0b10001,
            0b10001,
            0b10001,
            0b00000,
            0b01110,
            0b10001,
            0b00000
        ]
    }


    # Setup LCD Screen
    lcd = LCD(0x27, cols=20, lines=4)

    try:
        lcd.clear()
        lcd.setCursor(0, 0)
        lcd.write('Hello', justify=HD44780.JUSTIFY_CENTER)
        lcd.setCursor(3, 0)
        lcd.write('World', justify=HD44780.JUSTIFY_CENTER)
        time.sleep(2)

        lcd.clear()
        lcd.setCursor(0, 0)
        lcd.write('Check It Out!')
        lcd.setCursor(1, 0)
        lcd.write('Right Aligned!', justify=HD44780.JUSTIFY_RIGHT)
        lcd.setCursor(2, 0)
        lcd.write('Centered!', justify=HD44780.JUSTIFY_CENTER)
        lcd.setCursor(3, 0)
        lcd.write('XXXXXXXXFILLXXXXXXXX')
        time.sleep(2)

        lcd.clear()
        lcd.createChar(0, CUSTOM_CHARS[0])
        lcd.createChar(1, CUSTOM_CHARS[1])
        lcd.setCursor(0, 0)
        lcd.write('Custom Characters!', justify=HD44780.JUSTIFY_CENTER)
        lcd.writeRaw(0, 1, 8)
        lcd.writeRaw(1, 1, 9)
        lcd.writeRaw(0, 2, 9)
        lcd.writeRaw(0, 2, 8)
        time.sleep(2)

        while(1):
            pass

    except KeyboardInterrupt:
        pass

    lcd.cleanup()

if __name__ == '__main__':
    main()
