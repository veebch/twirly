
""" test example file for drv8825.py

 Note: Maximum step frequency is limited by the stepper motor physics.
       In microstepping-mode high(er) step frequencies may work fine!
"""

import sys
from time import sleep_ms
import drv8825_setup

def run_test(mot, enc, button):

    def action(revs, mode, speed):
        input(f"Press <Enter> to continue {revs=} {mode=} {speed=} ")
        mot.revolutions(revs, mode, speed)
        mot.enable()
        while mot.get_progress() > 0:       # if not all steps taken
            if button():            # button pressed
                mot.disable()
                break
            sleep_ms(50)                # wait
        return("OK")
#        return abs(revs * mot.steps_per_revolution - mot.get_progress())

    try:
        # full step variants, different speeds and directions
        # <number of steps>,<step type>, <step frequency>
        action( 1, "Full", 600)
        
    except KeyboardInterrupt:
        print("Interrupted from Keyboard")


# ===================MAIN===============================

print("TEST START")
if (enc := drv8825_setup.setup_rotary()) is None:
    print("No rotary encoder")
    sys.exit()
if (mot := drv8825_setup.setup_stepper()) is None:
    print("No stepper driver")
    sys.exit()
button, _, _ = drv8825_setup.setup_switches()
print(button)
run_test(mot, enc, button)
print("TEST END")

# =====================END===========================


