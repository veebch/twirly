"""
Micropython driver for bipolar stepper motor via DRV8825

This file licensed under the MIT License and incorporates work covered by
the following copyright and permission notice:

The MIT License (MIT)

Copyright (c) 2022-2023 Rob Hamerling

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Rob Hamerling, Version 0.3 September 2023

This driver was developed after some examples:
    https://github.com/gavinlyonsrepo/RpiMotorLib
    https://github.com/redoxcode/micropython-stepper

    Hardware wiring considerations of Microcontroller and DRV8825 board:
    Mandatory connections, to be specified as pin numbers:
    - STEP:     Stepper motor movement.
    Optional connections:
    - DIR:      Direction pin.
                When motor is used in only one direction this
                pin could be pulled high or low externally.
                Direction commands will be ignored.
    - M0,M1,M2: When it must be possible to select different
                microsteps all three pins must be connected
                and specified as a tuple.
                When microstepping is not required these
                pins of the DRV8825 may be left unconnected,
                in which case stepping is per full steps.
                The pins may also be pulled-up or pulled-down
                by external resistors, in which case stepping
                is always a fixed number of microsteps.
    - SLEEP, RESET: Must be pulled high by external resistors
                or should be connected and specified.
    - TIMER     Timer for stepping rate.

    Note: ENABLE pin of DRV8825 may be left unconnected or must be
          pulled low externally for the DRV8825 to become operational.

    Three modes of operation are forseen:
        - performing a number of steps
        - performing a number of full rotations
        - stepping indefinitely (until stopped)
    In all cases stepping direction, frequency and micro-stepping can be selected

"""

from machine import Pin, Timer
from time import sleep_ms
import utime


class DRV8825(object):
    """Class to control a bi-polar stepper motor with a DRV8825"""

    # dictionary with microstepping settings of pins (M0, M1, M2)
    microstep_dict = {
        1: (0, 0, 0),
        2: (1, 0, 0),
        4: (0, 1, 0),
        8: (1, 1, 0),
        16: (0, 0, 1),
        32: (1, 0, 1),
    }

    def __init__(
        self,
        step_pin,
        direction_pin=None,
        microstep_pins=None,
        sleep_pin=None,
        reset_pin=None,
        timer_id=-1,
        steps_per_revolution=200,
    ):
        """
        <step_pin>  (number) pin connected to STEP of DRV8825
        <direction_pin> (number) pin connected to DIR of DRV8825
        <microstep_pins> (tuple) 3 pins connected to M0,M1,M2 of DRV8825
                    for microstep resolution.
        <sleep_pin> (number) pin connected to SLEEP of DRV8825
        <reset_pin> (number) pin connected to RESET of DRV8825
        <timer_id>  (number) timer to use for step timing, the default
                    value -1 (last timer) usually works on most boards
        <steps_per_revolution> (number) Full steps for 360 degrees revolution
        Notes: - <step_pin> is mandatory.
               - other pins are optional (presumably fixed wired)
               - instances of DRV8825 are started enabled.
        """
        self._step_pin = Pin(step_pin, Pin.OUT)
        self._direction_pin = None
        if direction_pin is not None:
            self._direction_pin = Pin(direction_pin, Pin.OUT)
        self._microstep_pins = None
        if microstep_pins is not None:
            if len(microstep_pins) == 3:
                self._microstep_pins = [Pin(p, Pin.OUT) for p in microstep_pins]
            else:
                print("microstep_pins must be specified as tuple of 3 numbers")
        self._sleep_pin = None
        if sleep_pin is not None:
            self._sleep_pin = Pin(sleep_pin, Pin.OUT)
        self._reset_pin = None
        if reset_pin is not None:
            self._reset_pin = Pin(reset_pin, Pin.OUT)
        self.steps_per_revolution = steps_per_revolution  # full steps for 360 degrees
        self._timer = Timer(
            timer_id, mode=Timer.PERIODIC
        )  # interval timer for stepping
        self._timer_running = False  # timer is not running yet
        self._free_run_mode = 0  # not running free
        self._actual_pos = 0  # actual position
        self._target_pos = 0  # target position

    def enable(self):
        """Enable the DRV8825
        When pins for sleep and reset are not specified
        reset and sleep pins must be pulled high externally,
        Enable pin may be left unconnected or must be pulled
        low externally.
        """
        if self._sleep_pin is not None:
            self._sleep_pin.on()  # wake up
        if self._reset_pin is not None:
            self._reset_pin.on()  # leave reset state
        sleep_ms(3)  # datasheet: minimum 1.7 ms

    def disable(self):
        """Disable the DRV8825"""
        self.stop()  # stop stepping
        if self._sleep_pin is not None:
            self._sleep_pin.off()  # put asleep
        if self._reset_pin is not None:
            self._reset_pin.off()  # enter reset state

    def reset(self, state=True, interval=None):
        """Reset the DRV8825 (True) or undo previous reset (False)
        When interval (milliseconds) is specified
        the DRV8825 is reset pin for the specified
        time and then re-activated.
        Reset pin must have been specified with object creation.
        """
        if self._reset_pin is not None:  # reset pin is specified
            if interval is not None:  # interval specified
                self._reset_pin.off()
                sleep_ms(interval)  # milliseconds
                self._reset_pin.on()
            else:
                self._reset_pin.value(state)  # negative logic

    def stop(self):
        """Stop stepping, but keep motor enabled (in position),
        it prevents for example bouncing back from an endswitch.
        """
        self._timer.deinit()  # (running or not)
        self._timer_running = False

    def resolution(self, microsteps=1):
        """method to set step number of microsteps per full step
        <microsteps> supported values: 1,2,4,8,16,32
        """
        if self._microstep_pins is not None:
            microstep = __class__.microstep_dict.get(microsteps, (0, 0, 0))
            for i in range(3):
                self._microstep_pins[i].value(microstep[i])
            # print("M0,M1,M2: ", ",".join(["{:d}"
            #      .format(self._microstep_pins[m].value()) for m in range(3)]))
        return microsteps

    def one_step(self, direction):
        """perform one step (forward if direction > 0, backward if direction < 0)"""
        if direction > 0:
            self._direction_pin.on()   # BACK TO ORIGINAL: positive = HIGH
            utime.sleep_us(2)  # Direction setup time
            self._step_pin.on()  # actual step (rising edge)
            self._actual_pos += 1
            utime.sleep_us(2)  # Minimum 1.9us high pulse for DRV8825
            self._step_pin.off()
            utime.sleep_us(2)  # Minimum 1.9us low pulse for DRV8825
        elif direction < 0:
            self._direction_pin.off()  # BACK TO ORIGINAL: negative = LOW
            utime.sleep_us(2)  # Direction setup time
            self._step_pin.on()
            self._actual_pos -= 1
            utime.sleep_us(2)  # Minimum 1.9us high pulse for DRV8825
            self._step_pin.off()
            utime.sleep_us(2)  # Minimum 1.9us low pulse for DRV8825

    def _timer_callback(self, t):
        """determine if stepping action opportune
        if true perform one step forward or backward
        """
        if self._free_run_mode != 0:
            self.one_step(1 if self._free_run_mode > 0 else -1)
        elif self._target_pos != self._actual_pos:  # target not reached yet
            self.one_step(1 if self._target_pos > self._actual_pos else -1)

    def steps(self, steps, microsteps=1, stepfreq=200):
        """move stepper motor a number of steps:
        <steps> (number)
                Number of steps to take.
                Positive number: clockwise, negative: counter clockwise
        <microsteps> (integer)
                Supported values 1,2,4,8,16,32
        <stepfreq> (number)
                step frequency: (micro-)steps per second (Hz)
        """
        self.resolution(microsteps)  # microstepping (?)
        self.enable()  # enable drv8825 hardware
        self._free_run_mode = 0
        self._actual_pos = 0  # new starting point
        self._target_pos = steps  # new target (pos/neg)
        self._timer.init(freq=abs(stepfreq), callback=self._timer_callback)
        self._timer_running = True

    def revolutions(self, revolutions, microsteps=1, stepfreq=200):
        """move stepper motor a number of full revolutions:
        <revolutions> (number)
                Number of full (360 degrees) revolutions.
                Positive number: clockwise, negative: counter clockwise
        <microsteps> (integer)
                Supported values: 1,2,4,8,16,32
        <stepfreq> (number)
                step frequency: steps per second (Hz)
        """
        if microsteps not in __class__.microstep_dict:
            print("Supported microsteps: 1,2,4,8,16,32")
            microsteps = 1
        steps = revolutions * self.steps_per_revolution * microsteps
        self.steps(steps, microsteps, stepfreq)

    def freerun(self, stepfreq=200, microsteps=1):
        """keep stepper motor stepping indefinitely
        (until stopped explicitly)
        <stepfreq> (number)
                step frequency: steps per second (Hz)
                positive value: forward, negative: backward
        <microsteps> (integer)
                Supported values: 1,2,4,8,16,32
        """
        self._timer.deinit()  # disable timer
        self._timer_running = False
        if stepfreq == 0:  # motor stopped
            return
        self.enable()  # enable drv8825 hardware
        self.resolution(microsteps)
        self._free_run_mode = 1 if stepfreq > 0 else -1  # forward/backward
        self._timer.init(freq=abs(stepfreq), callback=self._timer_callback)
        self._timer_running = True
        return

    def get_progress(self):
        """getter method
        return steps taken so far to reach target (negative with CCW!)
        """
        if self._free_run_mode != 0:  # free running
            return 0  # what else to say?
        return self._actual_pos  # steps taken in 'this' operation

    # properties
    # By defining a property 'progress' it acts as an attribute
    # and can be used as <instance>.progress
    # note: there is no setter method!
    progress = property(get_progress)  # there is no set_progress!!


#

