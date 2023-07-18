# IR component based on code by Peter Hinch
# Copyright Peter Hinch 2020-2022 Released under the MIT licence

import time
import math
import _thread
import machine 
from ir_rx.print_error import print_error  # Optional print of error codes
from ir_rx.nec import NEC_16

# Motor drive module - PWM for speed control
A_1A_pin = 14
A_1B_pin = 15
A_1A = machine.PWM(machine.Pin(A_1A_pin, machine.Pin.OUT))
A_1B = machine.PWM(machine.Pin(A_1B_pin, machine.Pin.OUT))
A_1A.freq(1000) 
A_1B.freq(1000)
A_1A.duty_u16(0)

# Remote control buttons
BUTTONS = {
    0x04: "speed down",
    0x05: "stop",
    0x06: "speed up",
    0x1a: "hold ccw",
    0x1b: "hold cw",
    0x12: "reset"
}

def doaspin(direction, speed, moving):
    if direction == 'speed up':
        if moving == 0:
            # If the motor isn't moving, the speed buttons do micro adjustments
            pass
            # m.MotorRun('MA', 'forward', 100, .1)
        else:
            speed += 5
            speed = min(100, speed)
    elif direction == 'speed down':
        if moving == 0:
            # m.MotorRun('MA', 'backward', 100, .1)
            pass
        else:
            speed -= 5
            speed = max(0, speed)
    elif direction == 'hold cw':
        if moving == -1:
           m.MotorStop('MA', speed) 
        if moving != 1:
            print("motor A CW, speed ", speed, "%")
            # m.MotorHold('MA', 'forward', speed)
            pass
            moving = 1
    elif direction == 'hold ccw':
        if moving == 1:
           # m.MotorStop('MA', speed)
           pass
        if moving != -1:
            print("motor A CCW, speed ", speed, "%")
            # m.MotorHold('MA', 'backward', speed)
            pass
            moving = -1
    elif direction == 'stop':
        if moving != 0:
            # m.MotorStop('MA', speed)
            pass
            moving = 0
    elif direction == 'reset':
        machine.reset()
    
    return speed, moving

# User callback
def cb(data, addr, ctrl):
    if data == -1:  # NEC protocol sends repeat codes.
        pass
    else:
        direction = BUTTONS[data]
        _thread.start_new_thread(doaspin, (direction, speed, moving))
        time.sleep(.1)
        
def mainloop():
    previous = "untouched" 
    ir = NEC_16(p, cb)  # Instantiate receiver
    ir.error_function(print_error)  # Show debug information
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ir.close()
        

if __name__ == '__main__':
    speed = 100
    moving = 0
    p = machine.Pin(16, machine.Pin.IN)
    mainloop()

