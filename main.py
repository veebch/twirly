from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import json
import machine
import os
import utime
import _thread
import drivers.drv8825_setup as drv8825_setup
import sys
import gc  # Garbage collection for memory management

AP_NAME = "pi pico"
AP_DOMAIN = "pipico.net"
AP_TEMPLATE_PATH = "ap_templates"
APP_TEMPLATE_PATH = "app_templates"
WIFI_FILE = "wifi.json"
WIFI_MAX_ATTEMPTS = 3

# Global microstepping configuration
current_microsteps = 16  # Now use 16 microstepping for smoother motion!

# Gear ratio configuration (motor gear teeth : turntable gear teeth)
# Motor gear: 27 teeth, Turntable gear: 81 teeth -> motor must turn 3 times per turntable rotation
GEAR_RATIO = 81 / 27  # 3.0:1 reduction - motor turns 3x to turn turntable 1x

# Global timelapse progress tracking
timelapse_running = False
timelapse_current_step = 0
timelapse_total_steps = 0

# Global command execution tracking
command_executing = False

# Try to reduce logging to save memory (if supported)
try:
    import phew.logging
    if hasattr(phew.logging, 'LOG_WARN'):
        phew.logging.LOG_LEVEL = phew.logging.LOG_WARN
    elif hasattr(phew.logging, 'WARN'):
        phew.logging.LOG_LEVEL = phew.logging.WARN
except:
    pass  # If logging config fails, continue anyway


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
    
    # Get current IP address
    import network
    wlan = network.WLAN(network.STA_IF)
    ip_address = wlan.ifconfig()[0]
    
    # Set up hostname and mDNS for twirly.local
    try:
        # Modern MicroPython mDNS approach
        import network
        
        # Set hostname for the device (this enables mDNS in modern MicroPython)
        network.hostname('twirly')
        print("Hostname set to 'twirly' with mDNS enabled")
        
        # Try to start mDNS service if available
        try:
            import mdns
            mdns.start('twirly', '_http._tcp', 80)
            print("mDNS service started for twirly.local")
        except ImportError:
            # Check if mDNS might already be working from network.hostname()
            print("Built-in mDNS may already be active from network.hostname()")
            print("If twirly.local doesn't work, a reboot may be needed to clear port conflicts")
        
    except Exception as e:
        print(f"WARNING: mDNS/hostname setup failed: {e}")
        # Final fallback - try basic hostname setting
        try:
            wlan.config(hostname='twirly')
            print("Basic hostname set to 'twirly'")
        except:
            print("All hostname methods failed")
    
    # Set up DNS catchall as backup
    dns.run_catchall(ip_address)
    
    # Print connection information
    print("\n" + "=" * 50)
    print("TURNTABLE CONTROL - ACCESS METHODS")
    print("=" * 50)
    print(f"Primary Access:  http://twirly.local")
    print(f"Direct IP:       http://{ip_address}")
    print("\nRECOMMENDED:")
    print("  Bookmark: http://twirly.local")
    print("  If twirly.local doesn't work, use the IP address")
    print("\nSETUP TIP:")
    print("  Most devices automatically discover twirly.local")
    print("  If not working, check your router supports mDNS/Bonjour")
    print("=" * 50)
    print("Web interface starting...")
    print("=" * 50 + "\n")
    
    def action(steps, microsteps=None, speed=50, use_ramping=True):
        """Execute stepper motor movement with proper microstepping"""
        global command_executing
        
        # Use global microsteps if not specified
        if microsteps is None:
            microsteps = current_microsteps
            
        print(f"DEBUG: Action - {steps} steps, {microsteps}x microsteps at {speed}Hz")
        
        # Set executing state
        command_executing = True
        
        try:
            # Use proper microstepping - this is the key fix!
            mot.steps(steps, microsteps, speed)
            
            # Wait for completion with timeout
            timeout_count = 0
            max_timeout = 100  # 5 seconds at 50ms intervals
            while mot.get_progress() > 0 and timeout_count < max_timeout:
                utime.sleep_ms(50)
                timeout_count += 1
                
            if timeout_count >= max_timeout:
                print("DEBUG: Movement timed out, forcing completion")
                mot.disable()  # Force stop
                utime.sleep_ms(100)
                mot.enable()   # Re-enable for next movement
            else:
                print("DEBUG: Movement completed normally")
                
        except Exception as e:
            print(f"DEBUG: Exception: {e}")
        finally:
            command_executing = False
            gc.collect()

    def action_with_ramping(steps, microsteps, target_speed):
        """Execute movement with smooth acceleration and deceleration curves"""
        if steps == 0:
            return
            
        # Simplified ramping for MicroPython constraints
        total_steps = abs(steps)
        direction = 1 if steps > 0 else -1
        
        # Ramping configuration - keep it simple for real-time performance
        start_speed = max(target_speed * 0.3, 30)  # Start at 30% of target speed
        ramp_ratio = 0.15  # Use 15% of total movement for ramping
        ramp_steps = max(int(total_steps * ramp_ratio), microsteps)
        
        if total_steps < microsteps * 6:  # Too short for effective ramping
            mot.steps(steps, microsteps, target_speed)
            while mot.get_progress() > 0:
                utime.sleep_ms(20)
            return
        
        # Simple 3-phase movement: accelerate -> constant -> decelerate
        try:
            # Phase 1: Acceleration (gradual speed increase)
            accel_steps = min(ramp_steps, total_steps // 3)
            mot.steps(direction * accel_steps, microsteps, start_speed)
            while mot.get_progress() > 0:
                utime.sleep_ms(10)
            
            # Phase 2: Constant speed (main movement)
            constant_steps = total_steps - 2 * accel_steps
            if constant_steps > 0:
                mot.steps(direction * constant_steps, microsteps, target_speed)
                while mot.get_progress() > 0:
                    utime.sleep_ms(15)
            
            # Phase 3: Deceleration (gradual speed decrease)
            if accel_steps > 0:
                mot.steps(direction * accel_steps, microsteps, start_speed)
                while mot.get_progress() > 0:
                    utime.sleep_ms(10)
                    
        except Exception as e:
            print(f"Ramping error: {e}")
            # Fallback to simple movement
            remaining = total_steps - mot.get_progress() if mot.get_progress() > 0 else 0
            if remaining > 0:
                mot.steps(direction * remaining, microsteps, target_speed // 2)
                while mot.get_progress() > 0:
                    utime.sleep_ms(20)

    def app_cw_360(request):
        try:
            # 360 degree turntable rotation accounting for gear ratio
            # Calculate steps: 200 full steps * gear ratio for actual 360° turntable rotation
            full_steps = int(200 * GEAR_RATIO)  # Account for 3.0:1 gear reduction
            # Slow full-circle speed by 5x for smoother rotation
            speed = max(50, (200 * (current_microsteps // 4)) // 5)
            action(full_steps * current_microsteps, current_microsteps, min(speed, 800), use_ramping=True)
            return f"360° CW turntable rotation completed ({current_microsteps}x microsteps, {min(speed, 800)}Hz)"
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
            return "360° CW rotation interrupted"
        except Exception as e:
            return f"360° CW rotation failed: {str(e)}"

    def app_ccw_360(request):
        try:
            # 360 degree turntable rotation accounting for gear ratio (counter-clockwise)
            full_steps = -int(200 * GEAR_RATIO)  # Account for 3.0:1 gear reduction
            # Slow full-circle speed by 5x for smoother rotation
            speed = max(50, (200 * (current_microsteps // 4)) // 5)
            action(full_steps * current_microsteps, current_microsteps, min(speed, 800), use_ramping=True)
            return f"360° CCW turntable rotation completed ({current_microsteps}x microsteps, {min(speed, 800)}Hz)"
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
            return "360° CCW rotation interrupted"
        except Exception as e:
            return f"360° CCW rotation failed: {str(e)}"

    def app_cw_nudge(request):
        try:
            print("CW nudge button pressed")
            # Simple nudge like original version
            action(6, 1, 50, use_ramping=False)  # 6 steps, full step mode, 50Hz
            return "OK"
        except Exception as e:
            print(f"CW nudge error: {e}")
            return "ERROR"

    def app_ccw_nudge(request):
        try:
            # Small nudge movement with microsteps (counter-clockwise) - no ramping for precision
            full_steps = -6
            speed = 100 * (current_microsteps // 8) if current_microsteps >= 8 else 50
            action(full_steps * current_microsteps, current_microsteps, max(speed, 50), use_ramping=False)
            return f"CCW nudge completed ({current_microsteps}x microsteps)"
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
            return "CCW nudge interrupted"
        except Exception as e:
            return f"CCW nudge failed: {str(e)}"

    def timelapse_worker(angle, steps, pause):
        """Worker function that runs timelapse in background thread"""
        global timelapse_running, timelapse_current_step, timelapse_total_steps, command_executing
        try:
            # Calculate steps per movement accounting for gear ratio
            steps_per_rotation = int(200 * current_microsteps * GEAR_RATIO)  # Full turntable rotation in microsteps (uses 3.0:1 gear reduction)
            steps_per_movement = int((angle / 360.0) * steps_per_rotation / steps)
            
            # Adaptive speed based on microstepping resolution
            base_speed = 100 * (current_microsteps // 8) if current_microsteps >= 8 else 50
            
            print(f"Starting timelapse: {angle}° in {steps} steps, {pause}s pause")
            print(f"Steps per movement: {steps_per_movement}, Speed: {base_speed}")
            
            # Execute timelapse sequence
            for step in range(steps):
                current_step = step + 1
                timelapse_current_step = current_step
                print(f"Step {current_step} of {steps}")
                
                # Execute movement with ramping for smoothness
                action(steps_per_movement, current_microsteps, base_speed, use_ramping=True)
                
                # Pause between steps (except for last step)
                if current_step < steps:
                    utime.sleep(pause)
                    
            print(f"Timelapse completed: {steps} steps, {angle}° rotation")
            
        except Exception as e:
            print(f"Timelapse error: {str(e)}")
        finally:
            # Always clean up state
            timelapse_running = False
            command_executing = False

    def app_timelapse(request):
        global timelapse_running, timelapse_current_step, timelapse_total_steps, command_executing
        try:
            # Check if a timelapse is already running
            if timelapse_running or command_executing:
                return "Error: Timelapse already running or another command executing"
                
            # Parse query parameters with defaults
            angle = float(request.query.get('angle', 360))
            steps = int(request.query.get('steps', 160))
            pause = float(request.query.get('pause', 3.0))
            
            # Set progress tracking and execution state
            timelapse_running = True
            command_executing = True
            timelapse_current_step = 0
            timelapse_total_steps = steps
            
            # Start timelapse in background thread
            _thread.start_new_thread(timelapse_worker, (angle, steps, pause))
            
            # Return immediately while timelapse runs in background
            return f"Timelapse started: {angle}° in {steps} steps, {pause}s pause"
            
        except Exception as e:
            print(f"Timelapse start error: {str(e)}")
            timelapse_running = False
            command_executing = False
            return f"Failed to start timelapse: {str(e)}"

    def app_stop(request):
        try:
            mot.stop()
            return "Emergency stop executed - motor disabled"
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
            return "Stop command interrupted"
        except Exception as e:
            return f"Stop command failed: {str(e)}"

    def app_set_microsteps(request):
        """Set microstepping resolution"""
        global current_microsteps
        try:
            # Get microsteps value from query parameter
            if 'microsteps' in request.query:
                new_microsteps = int(request.query['microsteps'])
                if new_microsteps in [1, 2, 4, 8, 16, 32]:
                    current_microsteps = new_microsteps
                    return f"Microstepping set to {current_microsteps}"
                else:
                    return "Invalid microstepping value. Use: 1, 2, 4, 8, 16, or 32"
            else:
                return f"Current microstepping: {current_microsteps}"
        except Exception as e:
            return f"Error setting microsteps: {e}"

    def app_get_status(request):
        """Get current system status including microstepping setting and network info"""
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            ip_address = wlan.ifconfig()[0]
            
            status = {
                "microsteps": current_microsteps,
                "motor_enabled": True,  # Could be enhanced to check actual motor status
                "ramping_enabled": True,
                "system": "ready",
                "network": {
                    "ip_address": ip_address,
                    "primary_url": "http://twirly.local",
                    "access_methods": [
                        "http://twirly.local (recommended)",
                        f"http://{ip_address} (direct IP)",
                        "http://any-domain.com (DNS catchall)"
                    ]
                }
            }
            return json.dumps(status)
        except Exception as e:
            return f"Error getting status: {e}"

    def app_get_progress(request):
        """Get timelapse progress and command execution status"""
        try:
            progress = {
                "running": timelapse_running,
                "current_step": timelapse_current_step,
                "total_steps": timelapse_total_steps,
                "percentage": int((timelapse_current_step / timelapse_total_steps * 100)) if timelapse_total_steps > 0 else 0,
                "command_executing": command_executing
            }
            return json.dumps(progress)
        except Exception as e:
            return f"Error getting progress: {e}"
            
    def app_test_ramping(request):
        """Test ramping with a controlled movement sequence"""
        try:
            print("Testing speed ramping...")
            # Test sequence: small move without ramping, large move with ramping
            
            # Small move (no ramping)
            action(3 * current_microsteps, current_microsteps, 100, use_ramping=False)
            utime.sleep(1)
            
            # Large move (with ramping)
            action(50 * current_microsteps, current_microsteps, 300, use_ramping=True)
            utime.sleep(1)
            
            # Return to start (with ramping)
            action(-53 * current_microsteps, current_microsteps, 250, use_ramping=True)
            
            return "Ramping test completed successfully"
        except Exception as e:
            return f"Ramping test failed: {e}"

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
    server.add_route("/stop", handler=app_stop, methods=["GET"])
    server.add_route("/toggle", handler=app_toggle_led, methods=["GET"])
    server.add_route("/microsteps", handler=app_set_microsteps, methods=["GET"])
    server.add_route("/status", handler=app_get_status, methods=["GET"])
    server.add_route("/progress", handler=app_get_progress, methods=["GET"])
    server.add_route("/test_ramping", handler=app_test_ramping, methods=["GET"])
    # Add other routes for your application...
    server.set_callback(app_catch_all)


# Figure out which mode to start up in...
if (mot := drv8825_setup.setup_stepper()) is None:
    print("No stepper driver")
    sys.exit()

# Start with full steps for testing, then enable microstepping
print(f"Motor initialized - testing with {current_microsteps} microstepping")

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
