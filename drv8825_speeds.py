
""" test example file for drv8825.py

 Note: Maximum step frequency is limited by the stepper motor physics.
       In microstepping-mode high(er) step frequencies may work fine!
"""
import sys
from time import sleep_ms
import drv8825_setup                    # wiring of DRV8825

def run_test(mot, low, high):
    # run the stepper repeatedly at different speeds and modes
    def action(speed, mode):
        print(f"Running {speed=} {mode=}")
        mot.freerun(stepfreq=speed, stepmode=mode)
        print(f"Hit an end switch to continue with next test ")
        while True:
            if speed > 0 and high():
                break
            elif speed < 0 and low():
                break
            sleep_ms(100)
        while low() or high():          # wait for both switches released(
            sleep_ms(100)

    try:
        while True:
            action(  135, "Full")
    except KeyboardInterrupt:
        print("Interrupted from Keyboard")

    mot.disable()


# ===================MAIN===============================

print("TEST START")
if (mot := drv8825_setup.setup_stepper()) is None:
    print("No stepper driver")
    sys.exit()
_, low, high = drv8825_setup.setup_switches()
run_test(mot, low, high)
print("TEST END")

# =====================END===========================

