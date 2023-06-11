# IR component based on code by Peter Hinch
# Copyright Peter Hinch 2020-2022 Released under the MIT licen~e

import time
import math
import gc
import sys
import _thread
from machine import Pin, freq, I2C, SPI,reset
from ir_rx.print_error import print_error  # Optional print of error codes
from ir_rx.nec import NEC_16
from rp2 import PIO, StateMachine, asm_pio



class PCA9685:
    # Registers/etc.
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Reseting PCA9685") 
        self.write(self.__MODE1, 0x00)
    
    def write(self, cmd, value):
        "Writes an 8-bit value to the specified register/address"
        self.i2c.writeto_mem(int(self.address), int(cmd), bytes([int(value)]))
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (value, cmd))
      
    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        rdate = self.i2c.readfrom_mem(int(self.address), int(reg), 1)
        if (self.debug):
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, int(reg), rdate[0]))
        return rdate[0]
    
    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 12500000.0    # 12.5MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1)
        #print("oldmode = 0x%02X" %oldmode)
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)
        if (self.debug):
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
      
    def setServoPulse(self, channel, pulse):
        pulse = pulse * (4095 / 100)
        self.setPWM(channel, 0, int(pulse))
    
    def setLevel(self, channel, value):
        if (value == 1):
              self.setPWM(channel, 0, 4095)
        else:
              self.setPWM(channel, 0, 0)

class MotorDriver():
    def __init__(self, debug=False):
        self.debug = debug
        self.pwm = PCA9685()
        self.pwm.setPWMFreq(60)       
        self.MotorPin = ['MA', 0,1,2, 'MB',3,4,5, 'MC',6,7,8, 'MD',9,10,11]
        self.MotorDir = ['forward', 0,1, 'backward',1,0]
        self.ramptime = 2
        self.rampsteps = 10

    def MotorRun(self, motor, mdir, speed, runtime):
        if speed > 100:
            return
        
        mPin = self.MotorPin.index(motor)
        mDir = self.MotorDir.index(mdir)
        
        if (self.debug):
            print("set PWM PIN %d, speed %d" %(self.MotorPin[mPin+1], speed))
            print("set pin A %d , dir %d" %(self.MotorPin[mPin+2], self.MotorDir[mDir+1]))
            print("set pin b %d , dir %d" %(self.MotorPin[mPin+3], self.MotorDir[mDir+2]))

        self.pwm.setServoPulse(self.MotorPin[mPin+1], speed)        
        self.pwm.setLevel(self.MotorPin[mPin+2], self.MotorDir[mDir+1])
        self.pwm.setLevel(self.MotorPin[mPin+3], self.MotorDir[mDir+2])
        
        time.sleep(runtime)
        self.pwm.setServoPulse(self.MotorPin[mPin+1], 0)
        self.pwm.setLevel(self.MotorPin[mPin+2], 0)
        self.pwm.setLevel(self.MotorPin[mPin+3], 0)
    
    def MotorHold(self, motor, mdir, speed):
        mPin = self.MotorPin.index(motor)
        mDir = self.MotorDir.index(mdir)
        
        if (self.debug):
            print("set PWM PIN %d, speed %d" %(self.MotorPin[mPin+1], speed))
            print("set pin A %d , dir %d" %(self.MotorPin[mPin+2], self.MotorDir[mDir+1]))
            print("set pin b %d , dir %d" %(self.MotorPin[mPin+3], self.MotorDir[mDir+2]))
        
        for vel in [ x * speed / self.rampsteps for x in range(self.rampsteps+1)]:
            self.pwm.setServoPulse(self.MotorPin[mPin+1], vel)        
            self.pwm.setLevel(self.MotorPin[mPin+2], self.MotorDir[mDir+1])
            self.pwm.setLevel(self.MotorPin[mPin+3], self.MotorDir[mDir+2])
            time.sleep(self.ramptime/self.rampsteps)
        
    def MotorStop(self, motor, speed):
        mPin = self.MotorPin.index(motor)
        slowdown = [speed * (1 - x  / self.rampsteps)  for x in range(self.rampsteps+1)]
        for vel in slowdown:
            self.pwm.setServoPulse(self.MotorPin[mPin+1], vel)
            print("stopping",vel)
            time.sleep(self.ramptime/self.rampsteps)
        
def doaspin(direction):
    global speed
    m = MotorDriver()
    offset=.1
    print('offset:',float(offset))
    runfor=offset/3
    if direction=='speed up':
        speed = speed+5
        speed = min (100, speed)
    elif direction=='speed down':
        speed = speed-5
        speed = max(0, speed)
    elif direction=='hold cw':    
        print("motor A CW, speed ",speed,"%")
        m.MotorHold('MA', 'forward', speed)
    elif direction=='hold ccw':
        print("motor A CCW, speed ",speed,"%")
        m.MotorHold('MA', 'backward', speed)
    elif direction == 'stop':
        m.MotorStop('MA',speed)
    elif direction == 'reset':
        reset()
    print(speed,"%", direction)
    return 

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
    

# User callback
def cb(data, addr, ctrl):
    global previous   #bad practice to use globals, but it's the quick way to make persistent values here
    if data == -1  :  # NEC protocol sends repeat codes.
        pass
    else:
        previous = buttons[data]
    _thread.start_new_thread(doaspin,(previous,))
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
        
# Main Logic
speed=100
mainloop()



