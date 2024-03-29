from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import json
import machine
import os
import utime
import _thread
import drv8825_setup
import sys

AP_NAME = "pi pico"
AP_DOMAIN = "pipico.net"
AP_TEMPLATE_PATH = "ap_templates"
APP_TEMPLATE_PATH = "app_templates"
WIFI_FILE = "wifi.json"
WIFI_MAX_ATTEMPTS = 3


def machine_reset():
    utime.sleep(1)
    print("Resetting...")
    machine.reset()


def setup_mode():
    print("Entering setup mode...")

    def ap_index(request):
        if request.headers.get("host").lower() != AP_DOMAIN.lower():
            return render_template(
                f"{AP_TEMPLATE_PATH}/redirect.html", domain=AP_DOMAIN.lower()
            )

        return render_template(f"{AP_TEMPLATE_PATH}/index.html")

    def ap_configure(request):
        print("Saving wifi credentials...")

        with open(WIFI_FILE, "w") as f:
            json.dump(request.form, f)
            f.close()

        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(
            f"{AP_TEMPLATE_PATH}/configured.html", ssid=request.form["ssid"]
        )

    def ap_catch_all(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(
                f"{AP_TEMPLATE_PATH}/redirect.html", domain=AP_DOMAIN
            )

        return "Not found.", 404

    server.add_route("/", handler=ap_index, methods=["GET"])
    server.add_route("/configure", handler=ap_configure, methods=["POST"])
    server.set_callback(ap_catch_all)

    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)


def application_mode():
    print("Entering application mode.")
    onboard_led = machine.Pin("LED", machine.Pin.OUT)

    def action(steps, mode, speed):
        mot.steps(steps, mode, speed)
        while mot.get_progress() > 0:  # if not all steps taken
            mot.disable()
            break
            sleep_ms(50)  # wait

    def app_cw_360(request):
        try:
            # full step variants, different speeds and directions
            # <number of steps>, <step type>, <step frequency>
            action(810, "Full", 200)
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
        return "OK"

    def app_ccw_360(request):
        try:
            # full step variants, different speeds and directions
            # <number of steps>, <step type>, <step frequency>
            action(-810, "Full", 200)
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
        return "OK"

    def app_cw_nudge(request):
        try:
            # full step variants, different speeds and directions
            # <number of steps>, <step type>, <step frequency>
            action(6, "Full", 20)
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
        return "OK"

    def app_ccw_nudge(request):
        try:
            # full step variants, different speeds and directions
            # <number of steps>, <step type>, <step frequency>
            action(-6, "Full", 20)
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
        return "OK"

    def app_timelapse(request):
        try:
            # full step variants, different speeds and directions
            # <number of steps>, <step type>, <step frequency>
            # first ramp up
            steplength = 1
            for x in range(5):
                action(steplength, "Full", 20)
                utime.sleep(3)
                action(steplength, "Full", 20)
                utime.sleep(3)
                steplength = steplength + 1
            for x in range(124):
                action(6, "Full", 20)
                utime.sleep(3)
            for x in range(5):
                action(steplength, "Full", 20)
                utime.sleep(3)
                action(steplength, "Full", 20)
                utime.sleep(3)
                steplength = steplength - 1
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
        return "OK"

    def app_index(request):
        return render_template(f"{APP_TEMPLATE_PATH}/index.html")

    def app_toggle_led(request):
        onboard_led.toggle()
        return "OK"

    def app_catch_all(request):
        return "Not found.", 404

    server.add_route("/", handler=app_index, methods=["GET"])
    server.add_route("/cw_a_bit", handler=app_cw_nudge, methods=["GET"])
    server.add_route("/ccw_a_bit", handler=app_ccw_nudge, methods=["GET"])
    server.add_route("/ccw_360", handler=app_ccw_360, methods=["GET"])
    server.add_route("/cw_360", handler=app_cw_360, methods=["GET"])
    server.add_route("/timelapse", handler=app_timelapse, methods=["GET"])
    server.add_route("/toggle", handler=app_toggle_led, methods=["GET"])
    server.add_route("/temperature", handler=app_get_temperature, methods=["GET"])
    server.add_route("/reset", handler=app_reset, methods=["GET"])
    # Add other routes for your application...
    server.set_callback(app_catch_all)


# Figure out which mode to start up in...
if (mot := drv8825_setup.setup_stepper()) is None:
    print("No stepper driver")
    sys.exit()
try:
    os.stat(WIFI_FILE)

    # File was found, attempt to connect to wifi...
    with open(WIFI_FILE) as f:
        wifi_current_attempt = 1
        wifi_credentials = json.load(f)

        while wifi_current_attempt < WIFI_MAX_ATTEMPTS:
            ip_address = connect_to_wifi(
                wifi_credentials["ssid"], wifi_credentials["password"]
            )

            if is_connected_to_wifi():
                print(f"Connected to wifi, IP address {ip_address}")
                break
            else:
                wifi_current_attempt += 1

        if is_connected_to_wifi():
            application_mode()
        else:
            # Bad configuration, delete the credentials file, reboot
            # into setup mode to get new credentials from the user.
            print("Bad wifi connection!")
            print(wifi_credentials)
            os.remove(WIFI_FILE)
            machine_reset()

except Exception:
    # Either no wifi configuration file found, or something went wrong,
    # so go into setup mode.
    setup_mode()

# Start the web server...
server.run()
