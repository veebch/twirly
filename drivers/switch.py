"""
    class for mechanical switches (micro switches, push buttons and alike)
    with rudimentary support for debouncing.
    The Pins for the switches are configured as Pin.IN and Pin.PULL_UP.
    The (normally-open) switches are supposed to make ground contact
    (falling interrupts are used).
"""

from machine import Pin
from time import ticks_ms

class Switch(object):
    def __init__(self, switch):
        """ <switch> (number) GPIO pin """
        self._switch = Pin(switch, Pin.IN, Pin.PULL_UP)
        self._switch_interrupt = False              # set by switch-ISR, reset by switch() method
        self._debounce_ticks_ms = ticks_ms()        # remember last switch interrupt time
        try:
            self._interrupt = self._switch.irq(trigger=Pin.IRQ_FALLING, handler=self._callback, hard=True)
        except TypeError:
            self._interrupt = self._switch.irq(trigger=Pin.IRQ_FALLING, handler=self._callback)

    def _callback(self, switch):
        """ Pin interrupt service routine """
        if (ticks_ms() - self._debounce_ticks_ms) > 500:    # skip switch bounces
            self._switch_interrupt = True           # mark 'interrupt occurred'
            self._debounce_ticks_ms = ticks_ms()    # update time of last accepted interrupt

    def switch(self):
        """ Indicator of Pin interrupt
            True: interrupt occurred since last poll, False: not!
        """
        if self._switch_interrupt:
            self._switch_interrupt = False          # user is aware of interrupt
            return True                             # signal switch interrupt
        return False

    def __call__(self):
        """ make switch instance callable """
        return self.switch()

