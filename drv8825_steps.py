
""" test example file for drv8825.py

 Note: Maximum step frequency is limited by the stepper motor physics.
       In microstepping-mode high(er) step frequencies may work fine!
"""

import sys
from time import sleep_ms
import drv8825_setup                    # wiring of DRV8825 and rotary encoder

def cw_nudge():

    def action(steps, mode, speed):
        mot.steps(steps, mode, speed)
        while mot.get_progress() > 0:       # if not all steps taken
            mot.disable()
            break
            sleep_ms(50)                # wait
        return "OK"
    try:
        # full step variants, different speeds and directions
        # <number of steps>, <step type>, <step frequency>
        action( 6, "Full", 20  )
    except KeyboardInterrupt:
        print("Interrupted from Keyboard")



# ===================MAIN===============================

print("TEST START")
if (mot := drv8825_setup.setup_stepper()) is None:
    print("No stepper driver")
    sys.exit()
(button, _,  _) = drv8825_setup.setup_switches()
cw_nudge()
print("TEST END")

# =====================END===========================

