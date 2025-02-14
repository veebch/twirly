
"""
    Example for drv8825 with position control by rotary encoder
"""

import sys
import drv8825_setup

def perform(mot, enc):
    try:
        cur_pos = enc.position(0)           # set initial
        print("Control stepper motor speed and direction by turning the rotary")
        while True:
            if (new_pos := enc.position() // 4) != cur_pos:   # only full encoder steps
                mot.steps((new_pos - cur_pos) * 10, "Full", 200)
                print(f"RPM {new_pos}")
                cur_pos = new_pos
    except KeyboardInterrupt:
        print("Interrupted from Keyboard")
    mot.disable()


# ===================MAIN===============================
def main():
    """ mainline """
    if (enc := drv8825_setup.setup_rotary()) is None:
        print("No rotary encoder")
        return
    if (mot := drv8825_setup.setup_stepper()) is None:
        print("No stepper driver")
        return

    perform(mot, enc)


print("Stepper motor control by DRV8825 and rotary encoder")
main()
print("Terminated")

