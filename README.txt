================
RPiLiquidCrystal
================

A port of the Arduino LiquidCrystal library to Python for use with the Raspberry Pi.
Typical usage often looks like this::

    #!/usr/bin/env python

    from RPiLiquidCrystal.LCD import LCD

    lcd = LCD(rs, enable, [d4, d5, d6, d7], backlight=backlight, lines=2)
    lcd.enableBacklight(90)
    lcd.clear()
    lcd.home()
    lcd.setCursor(0, 0)
    lcd.printMessage('Hello')
    lcd.setCursor(0, 1)
    lcd.printMessage('World')

Initialize
==========

The RPiLiquidCrystal library assumes 4-bit mode, because who would use 8 data lines!
This library can be used for a wired interface, as well as an i2C interface.

Initializing for a wired interface::

    lcd = LCD(rs, enable, [d4, d5, d6, d7])

Initializing for an i2C interface::

    lcd = LCD(0x27)

R/W Pin
-------
If an R/W pin is to be used, you can set it in the optional parameters (for the wired interface only)::

    lcd = LCD(rs, enable, [d4, d5, d6, d7], rw=rw)

Optional Arguments
------------------
You can set the number of columns (cols), lines, and pixel font height (5x10 sections instead of 5x8)

    lcd = LCD(rs, enable, [d4, d5, d6, d7], cols=16, lines=2, dotsize=10)

    or

    lcd = LCD(0x27, cols=20, lines=4)

Contributors
============

Fernando Chorney

