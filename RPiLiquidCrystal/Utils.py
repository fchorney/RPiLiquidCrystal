import time

def delay_microseconds(microseconds):
    seconds = float(microseconds) * 0.000001
    time.sleep(seconds)
