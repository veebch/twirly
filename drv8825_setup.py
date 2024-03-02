"""
    setup for DRV8825 examples on some specific boards
    DRV8825, rotary-encoder and end switches wiring with ESP32 and RP2
 """

import sys
from machine import Pin
from drv8825 import DRV8825


def setup_stepper():
    """setup for DRV8825 stepper driver, returns an instance or None"""
    if sys.platform == "esp32":  # ====== ESP32 wiring ====
        direction_pin = 2  # DIR
        step_pin = 5  # STEP
        sleep_pin = 18  # SLEEP
        reset_pin = 23  # RESET
        resolution_pins = (4, 22, 19)  # (M0, M1, M2) tuple
    elif sys.platform == "rp2":  # ====== RP2040 pico wiring ====
        direction_pin = 6  # DIR
        step_pin = 7  # STEP
        sleep_pin = 8  # SLEEP
        reset_pin = 9  # RESET
        resolution_pins = (12, 11, 10)  # (M0, M1, M2) tuple
    else:
        print("Provide pin wiring of DRV8825 for", sys.platform)
        return None
    # Instance of DRV8825 class
    return DRV8825(step_pin, direction_pin, resolution_pins, sleep_pin, reset_pin)


#
