# IR component based on code by Peter Hinch
# Copyright Peter Hinch 2020-2022 Released under the MIT licence

import time
import math
import _thread
import machine 
from ir_rx.print_error import print_error  # Optional print of error codes
from ir_rx.nec import NEC_16

# Motor drive module - PWM for speed control
IN_C_pin = 14
IN_D_pin = 15
IN_C = machine.PWM(machine.Pin(IN_C_pin, machine.Pin.OUT))
IN_D = machine.PWM(machine.Pin(IN_D_pin, machine.Pin.OUT))
IN_C.freq(1000) 
IN_D.freq(1000)
IN_C.duty_u16(0) 
IN_D.duty_u16(0)

# Remote control buttons
BUTTONS = {
    0x04: "speed down",
    0x05: "stop",
    0x06: "speed up",
    0x1a: "hold ccw",
    0x1b: "hold cw",
    0x12: "reset"
}

irpower = machine.Pin(0, machine.Pin.OUT)
irpower.value(1)

def updatespeed(speed,moving):
    if moving == 1:
        IN_C.duty_u16(int((speed/100)*65025))
        IN_D.duty_u16(0)
    if moving == - 1:
        IN_C.duty_u16(0)
        IN_D.duty_u16(int((speed/100)*65025))
        
        
def stopmotor(speed,moving):
    for i in range (speed, 0, -5):
        print("stop")
        print(i)
        if moving == 1:
            IN_C.duty_u16(int((i/100)*65025))
            IN_D.duty_u16(0)
        if moving == - 1:
            IN_C.duty_u16(0)
            IN_D.duty_u16(int((i/100)*65025))
        time.sleep(.1)
        IN_C.duty_u16(0)
        IN_D.duty_u16(0)
    return
            
def rampup(speed, moving):
    for i in range (15, speed, 5):
        sp = i+5
        print(sp)
        if moving == 1:
            IN_C.duty_u16(int((sp/100)*65025))
            IN_D.duty_u16(0)
        if moving == -1:
            IN_C.duty_u16(0)
            IN_D.duty_u16(int((sp/100)*65025))
        time.sleep(.1)


def doaspin(command):
    global speed
    global moving
    print(command, speed, moving)
    if command == 'speed up':
        if moving == 0:
            # If the motor isn't moving, the speed buttons do small adjustments
            pass
            # nudge cw
        else:
            speed += 5
            speed = min(100, speed)
            updatespeed(speed, moving)
    elif command == 'speed down':
        if moving == 0:
            # nudge ccw
            pass
        else:
            speed -= 5
            speed = max(0, speed)
            updatespeed(speed, moving)
            if speed == 0:
                moving = 0
    elif command == 'hold cw':
        if moving == -1:
           stopmotor(speed, moving)
        if moving != 1:
            print("motor A CW, speed ", speed, "%")
            moving = 1 # CW
            rampup(speed, moving)
    elif command == 'hold ccw':
        if moving == 1:
           stopmotor(speed, moving)
        if moving != -1:
            print("motor A CCW, speed ", speed, "%")
            moving = -1 # CCW
            rampup(speed, moving)
    elif command == 'stop':
        stopmotor(speed, moving)
        moving = 0
    elif command == 'reset':
        machine.reset()
    return speed, moving

# User callback
def cb(data, addr, ctrl):
    if data == -1:  # NEC protocol sends repeat codes.
        pass
    else:
        command = BUTTONS[data]
        _thread.start_new_thread(doaspin, (command,))
        time.sleep(.1)
        
def mainloop():
    previous = "untouched" 
    ir = NEC_16(p, cb)  # Instantiate receiver
    ir.error_function(print_error)  # Show debug information
    try:
        while True:
            time.sleep(1)
    except:
        ir.close()
        IN_C.duty_u16(0) 
        IN_D.duty_u16(0)
        

if __name__ == '__main__':
    speed = 100
    # moving 0 = stopped, 1 = clockwise, -1 = counter clockwise
    moving = 0
    p = machine.Pin(16, machine.Pin.IN)  
    mainloop()

