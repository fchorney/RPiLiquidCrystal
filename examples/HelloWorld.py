#!/usr/bin/env python

import RPIO as GPIO
import time
from RPiLiquidCrystal.HD44780 import HD44780
from RPiLiquidCrystal.LCD import LCD


def main():
    # Rewrite pins for your own specification
    RS          = 17
    ENABLE      = 25
    BACKLIGHT   = 18
    D4          = 27
    D5          = 24
    D6          = 22
    D7          =  4

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
    lcd = LCD(
        RS, ENABLE, [D4, D5, D6, D7],
        backlight=BACKLIGHT, lines=2
    )

    try:
        lcd.enableBacklight()

        lcd.clear()
        lcd.setCursor(0, 0)
        lcd.write('Hello', justify=HD44780.JUSTIFY_CENTER)
        lcd.setCursor(1, 0)
        lcd.write('World', justify=HD44780.JUSTIFY_CENTER)
        time.sleep(2)

        lcd.clear()
        lcd.setCursor(0, 0)
        lcd.write('Check It Out!')
        lcd.setCursor(1, 0)
        lcd.write('Right Aligned!', justify=HD44780.JUSTIFY_RIGHT)
        time.sleep(2)

        lcd.clear()
        lcd.createChar(0, CUSTOM_CHARS[0])
        lcd.createChar(1, CUSTOM_CHARS[1])
        lcd.setCursor(0, 0)
        lcd.write('Custom Characters!', justify=HD44780.JUSTIFY_CENTER)
        lcd.writeRaw(0, 1, 7)
        lcd.writeRaw(1, 1, 8)
        time.sleep(2)

        def _write_percentage(percentage):
            lcd.setBrightness(percentage)
            lcd.setCursor(0, 0)
            lcd.write('Backlight Test', justify=HD44780.JUSTIFY_CENTER)
            lcd.setCursor(1, 0)
            lcd.write(
                'Width: %%%03d' % percentage, justify=HD44780.JUSTIFY_CENTER
            )
            lcd.writeRaw(0, 1, 0)
            lcd.writeRaw(1, 1, 15)

        while 1:
            for i in range(0, 100, 1):
                _write_percentage(i)
                time.sleep(0.02)

            for i in range(100, 0, -1):
                _write_percentage(i)
                time.sleep(0.02)

    except KeyboardInterrupt:
        pass
    lcd.cleanup()
    GPIO.cleanup()

if __name__ == '__main__':
    main()
