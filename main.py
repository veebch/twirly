""" Test of stepper

 Note: Maximum step frequency is limited by the stepper motor physics.
       In microstepping-mode high(er) step frequencies may work fine!
"""

import sys
import utime
import drv8825_setup


def run_test(mot, enc, button):
    def action(revs, mode, speed):
        input(f"Press <Enter> to continue {revs=} {mode=} {speed=} ")
        mot.revolutions(revs, mode, speed)

        return abs(revs * mot.steps_per_revolution - mot.progress)

    try:
        # full step variants, different speeds and directions
        # <number of steps>, <step type>, <step frequency>
        action(1, "Full", 50)
        action(-1, "Full", 100)
        action(5, "Full", 400)
        action(-5, "Full", 600)
        # microstepping variants
        action(1, "Half", 500)
        action(-1, "1/4", 1000)
        action(5, "1/8", 2000)
        action(-5, "1/16", 4000)
        action(3, "1/32", 8000)
    except KeyboardInterrupt:
        print("Interrupted from Keyboard")

    mot.disable()


# ===================MAIN===============================

print("TEST START")
button = None
if (mot := drv8825_setup.setup_stepper()) is None:
    print("No stepper driver")
    sys.exit()
enc = None
print(mot)

run_test(mot, enc, button)

print("TEST END")

# =====================END===========================

