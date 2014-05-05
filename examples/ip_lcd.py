#!/usr/bin/env python

import sys
import argparse
from RPiLiquidCrystal.LCD_i2C import LCD

def main():
    args = parse_args()

    # Setup LCD Screen
    lcd = LCD(0x27, cols=20, lines=4)

    try:
        lcd.clear()
        lcd.setCursor(0, 0)
        lcd.write('w0 %s' % args.wip)
        lcd.setCursor(1, 0)
        lcd.write('%s' % args.ssid)
        lcd.setCursor(2, 0)
        lcd.write('e0 %s' % args.ip)
        lcd.setCursor(3, 0)
        lcd.write('%s' % args.plugstatus)
    except KeyboardInterrupt:
        pass

    lcd.cleanup()
    sys.exit(0)

def parse_args():
    parser = argparse.ArgumentParser(description='displays eth0 and wlan0 \
    status on 4x20 LCD Display')

    parser.add_argument('ssid', type=str, help='wireless ssid')
    parser.add_argument('wip', type=str, help='wireless ip')
    parser.add_argument('plugstatus', type=str, help='wired plug status')
    parser.add_argument('ip', type=str, help='wired ip')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()
