"""
    setup for DRV8825 examples on some specific boards
    DRV8825, rotary-encoder and end switches wiring with ESP32 and RP2
 """

import sys
from machine import Pin
from .encoder_portable import Encoder
from .drv8825 import DRV8825
from .switch import Switch


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
        resolution_pins = (12, 11, 10)  # (M0, M1, M2) tuple - microstepping enabled!
    else:
        print("Provide pin wiring of DRV8825 for", sys.platform)
        return None
    # Instance of DRV8825 class
    return DRV8825(step_pin, direction_pin, resolution_pins, sleep_pin, reset_pin)


def setup_rotary():
    """setup for rotary encoder, returns an instance or None"""
    if sys.platform == "esp32":  # ====== ESP32 wiring ====
        sw1 = Pin(32, Pin.IN)
        sw2 = Pin(35, Pin.IN)
    elif sys.platform == "rp2":  # ====== RP2040 wiring ====
        sw1 = Pin(0, Pin.IN)
        sw2 = Pin(1, Pin.IN)
    else:
        print("Provide pin wiring of rotary encoder for", sys.platform)
        return None
    return Encoder(sw1, sw2)  # rotary with push button


def setup_switches():
    """setup for 2 end switches, returns a tuple or None"""
    if sys.platform == "esp32":  # ====== ESP32 wiring ====
        button = Switch(34)
        switch1 = Switch(13)
        switch2 = Switch(15)
    elif sys.platform == "rp2":  # ====== RP2040 wiring ====
        button = Switch(2)
        switch1 = Switch(14)
        switch2 = Switch(15)
    else:
        print("Provide pin wiring of end switch for", sys.platform)
        return (None, None, None)
    return (button, switch1, switch2)  # end switches


#

