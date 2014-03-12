================
RPiLiquidCrystal
================

A port of the Arduino LiquidCrystal library to Python for use with the Raspberry Pi.
Typical usage often looks like this::

    #!/usr/bin/env python

    from RPiLiquidCrystal import LCD

    lcd = LCD(rs, enable, [d4, d5, d6, d7], fourbitmode=True, lines=2)
    lcd.clear()
    lcd.home()
    lcd.setCursor(0, 0)
    lcd.printMessage('Hello')
    lcd.setCursor(0, 1)
    lcd.printMessage('World')

Initialize
==========

The RPiLiquidCrystal library can be initialized in either 8-bit mode or 4-bit mode
(this corresponds to the number of data lines available).

Initializing for a 4-bit interface::

    lcd = LCD(rs, enable, [d4, d5, d6, d7], fourbitmode=True)

Initializing for an 8-bit interface::

    lcd = LCD(rs, enable, [d0, d1, d2, d3, d4, d5, d6, d7])

R/W Pin
-------
If an R/W pin is to be used, you can set it in the optional parameters::

    lcd = LCD(rs, enable, [d4, d5, d6, d7], fourbitmode=True, rw=rw)

Optional Arguments
------------------
You can set the number of columns (cols), lines, and pixel font height (5x10 sections instead of 5x8)

    lcd = LCD(rs, enable, [d4, d5, d6, d7], fourbitmode=True, cols=16, lines=2, dotsize=10)

Contributors
============

Fernando Chorney

