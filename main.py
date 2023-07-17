# IR component based on code by Peter Hinch
# Copyright Peter Hinch 2020-2022 Released under the MIT licence

import time
import math
import _thread
import machine 
from ir_rx.print_error import print_error  # Optional print of error codes
from ir_rx.nec import NEC_16

A_1A_pin = 13                       # Motor drive module
A_1B_pin = 14                       # Motor drive module (any of the pins can be driven by PWM)
A_1A = machine.PWM(Pin(A_1A_pin))
A_1B = machine.PWM(Pin(A_1B_pin))
  
# Remote control stuff
# If you're using a different one (you probably are) use the test.py file in the ir_rx directory to get the values for your remote

# Set Power Pin
pin = machine.Pin(0, machine.Pin.OUT)
pin.value(1)

p = Pin(16, Pin.IN)
buttons = {
    0x04:"speed down",
    0x05:"stop",
    0x06:"speed up",
    0x1a:"hold ccw",
    0x1b:"hold cw",
    0x12:"reset"}

def doaspin(direction):
    global speed    # Globals...deep shame
    global moving
    if direction=='speed up':
        if moving==0:
            # If the motor isn't moving, the speed buttons do micro adjustmnets
            # m.MotorRun('MA','forward',100,.1)
        else:
            speed = speed+5
            speed = min (100, speed)
    elif direction=='speed down':
        if moving==0:
            # m.MotorRun('MA','backward',100,.1)
        else:
            speed = speed-5
            speed = max(0, speed)
    elif direction=='hold cw':
        if moving == -1:
           m.MotorStop('MA',speed) 
        if moving !=1:
            print("motor A CW, speed ",speed,"%")
            # m.MotorHold('MA', 'forward', speed)
            moving = 1
    elif direction=='hold ccw':
        if moving == 1:
           # m.MotorStop('MA',speed) 
        if moving !=-1:
            print("motor A CCW, speed ",speed,"%")
            # m.MotorHold('MA', 'backward', speed)
            moving = -1
    elif direction == 'stop':
        if moving != 0:
            # m.MotorStop('MA',speed)
            moving = 0
    elif direction == 'reset':
        machine.reset()
    return 

# User callback
def cb(data, addr, ctrl):
    global previous   
    if data == -1  :  # NEC protocol sends repeat codes.
        pass
    else:
        previous = buttons[data]
    _thread.start_new_thread(doaspin,(previous,))
    time.sleep(.1)
        
def mainloop():
    speed=100
    moving=0
    previous = "untouched" 
    ir = NEC_16(p, cb)  # Instantiate receiver
    ir.error_function(print_error)  # Show debug information
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ir.close()
        

if __name__ == '__main__':
    mainloop()