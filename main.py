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
current_microsteps = 32  # Maximum 32x microstepping for ultra-smooth, quiet operation!

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

        # Schedule reboot to attempt connection with new credentials
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
    
    # Get current IP address with retry logic for CYW43 stability
    import network
    wlan = network.WLAN(network.STA_IF)
    
    # Add retry logic for network interface issues
    ip_address = None
    for attempt in range(3):
        try:
            ip_address = wlan.ifconfig()[0]
            if ip_address and ip_address != '0.0.0.0':
                break
        except Exception as e:
            print(f"Network interface error (attempt {attempt+1}): {e}")
            if attempt < 2:
                import utime
                utime.sleep(2)  # Wait before retry
    
    if not ip_address or ip_address == '0.0.0.0':
        print("ERROR: Could not get valid IP address - network may be unstable")
        ip_address = "unknown"
    
    # Set hostname and use lwIP's built-in mDNS (if available) - but be gentle with CYW43
    hostname_set = False
    try:
        # The Pico W defaults to 'picow.local' which works well
        # No need to override - just verify it's working
        if ip_address and ip_address != "unknown":
            import lwip_mdns
            if lwip_mdns.setup_lwip_mdns('picow'):  # Use default hostname
                print("Hostname and mDNS configured (using picow.local)")
                hostname_set = True
            else:
                print("WARNING: Hostname setup had issues")
    except Exception as e:
        print(f"ERROR: Hostname/mDNS setup error: {e}")
    
    # Fallback to basic hostname setting if needed
    if not hostname_set and ip_address != "unknown":
        try:
            wlan.config(hostname='picow')  # Ensure default hostname
            print("Basic hostname confirmed as 'picow'")
            hostname_set = True
        except Exception as e2:
            print(f"ERROR: Even basic hostname failed: {e2}")
    
    # Temporarily disable custom mDNS to avoid socket conflicts with lwIP
    print("INFO: Custom mDNS announcer disabled to avoid lwIP conflicts")
    # Skip custom mDNS if network is unstable to avoid overloading CYW43
    if False:  # Temporarily disabled
        if ip_address == "unknown":
            print("WARNING: Skipping mDNS due to network instability")
        else:
            # Only use minimal mDNS announcer if network seems stable
            try:
                import mdns_announcer
                if mdns_announcer.start_mdns_announcer('twirly', ip_address, 180):  # Longer interval
                    print("mDNS announcer started (reduced frequency)")
            except Exception as e:
                print(f"INFO: mDNS announcer not started: {e}")
    
    if not hostname_set:
        print("WARNING: No hostname configured - use IP address directly")
    
    # Set up DNS catchall as backup (but only if network is stable)
    if ip_address != "unknown":
        try:
            dns.run_catchall(ip_address)
            print("DNS catchall configured")
        except Exception as e:
            print(f"WARNING: DNS catchall failed: {e}")
    
    # Print connection information
    print("\n" + "=" * 50)
    print("TWIRLY WEB INTERFACE READY")
    print("=" * 50)
    if ip_address != "unknown":
        print(f"Primary: http://picow.local")
        print(f"Backup:  http://{ip_address}")
        try:
            ssid = wlan.config('ssid')
            print(f"Network: {ssid}")
        except:
            print("Network: Connected (SSID unavailable)")
        print("\nAccess Methods:")
        print("1. http://picow.local (mDNS hostname)")
        print(f"2. http://{ip_address} (direct IP)")
        print("3. Point any domain to this IP (DNS catchall)")
    else:
        print("WARNING: Network interface unstable")
        print("Check CYW43 WiFi chip status")
        print("May need device restart")
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
            # Small nudge movement with microsteps (clockwise) - no ramping for precision
            full_steps = 6
            speed = 100 * (current_microsteps // 8) if current_microsteps >= 8 else 50
            action(full_steps * current_microsteps, current_microsteps, max(speed, 50), use_ramping=False)
            return f"CW nudge completed ({current_microsteps}x microsteps)"
        except KeyboardInterrupt:
            print("Interrupted from Keyboard")
            return "CW nudge interrupted"
        except Exception as e:
            return f"CW nudge error: {e}"

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
        
        current_step = 0
        
        try:
            print(f"Starting timelapse: {angle}° in {steps} steps, {pause}s pause")
            
            # Calculate steps per movement accounting for gear ratio
            steps_per_rotation = int(200 * current_microsteps * GEAR_RATIO)
            steps_per_movement = int((angle / 360.0) * steps_per_rotation / steps)
            
            # Ensure minimum movement for very small angles
            if steps_per_movement == 0:
                steps_per_movement = 1
                print("Warning: Using minimum 1 microstep per movement")
            
            # Handle negative angles for direction
            if angle < 0:
                steps_per_movement = -abs(steps_per_movement)
            else:
                steps_per_movement = abs(steps_per_movement)
            
            # Speed calculation
            base_speed = 400 if current_microsteps >= 32 else 200
            
            print(f"Movement: {steps_per_movement} microsteps at {base_speed}Hz per step")
            
            # Execute timelapse sequence
            for step in range(steps):
                if not timelapse_running:
                    break
                    
                current_step = step + 1
                timelapse_current_step = current_step
                print(f"Step {current_step} of {steps}")
                
                # Direct motor control to avoid command_executing flag conflicts
                try:
                    print(f"DEBUG: Timelapse step {current_step} - {steps_per_movement} microsteps at {base_speed}Hz")
                    mot.steps(steps_per_movement, current_microsteps, base_speed)
                    
                    # Wait for completion
                    timeout_count = 0
                    max_timeout = 100
                    while mot.get_progress() > 0 and timeout_count < max_timeout:
                        # Use simple loop for timing to avoid any scoping issues
                        for i in range(5000):
                            pass
                        timeout_count += 1
                        
                    print(f"DEBUG: Step {current_step} movement completed")
                except Exception as e:
                    print(f"Movement error in step {current_step}: {e}")
                
                # Pause between steps (except for last step)
                if current_step < steps and timelapse_running:
                    print(f"Pausing {pause}s...")
                    # Simple busy wait loop - no function calls that might have scoping issues
                    pause_loops = int(pause * 500000)  # Approximate timing
                    for wait_count in range(pause_loops):
                        if not timelapse_running:
                            break
                    
            print(f"Timelapse completed: {steps} steps")
            
        except Exception as e:
            print(f"Timelapse error at step {current_step}: {str(e)}")
        finally:
            # Ensure all flags are cleared with more robust cleanup
            print("Starting timelapse cleanup...")
            timelapse_running = False
            command_executing = False
            timelapse_current_step = 0
            timelapse_total_steps = 0
            print("All timelapse flags cleared")
            
            # Longer delay to ensure web interface has time to poll and see the changes
            for i in range(50000):  # Increased delay
                pass
            
            # Force garbage collection
            gc.collect()
            print("Timelapse cleanup complete")

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
        global timelapse_running, command_executing
        try:
            # Stop any running timelapse
            timelapse_running = False
            command_executing = False
            
            # Emergency stop motor
            mot.stop()
            print("Emergency stop: all operations halted")
            return "Emergency stop executed - motor disabled, timelapse stopped"
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
                    "primary_url": "http://picow.local",
                    "access_methods": [
                        "http://picow.local (recommended)",
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
            print(f"DEBUG: Progress - running={timelapse_running}, step={timelapse_current_step}/{timelapse_total_steps}, executing={command_executing}")
            return json.dumps(progress)
        except Exception as e:
            return f"Error getting progress: {e}"
            
    def app_debug_mdns(request):
        """Debug mDNS functionality"""
        return """<!DOCTYPE html>
<html>
<head><title>mDNS Debug</title></head>
<body>
<h1>mDNS Debug - Simplified</h1>
<p>The system now uses <strong>picow.local</strong> as the default hostname.</p>
<p>Try accessing: <a href="http://picow.local">http://picow.local</a></p>
<p><a href="/">Back to Home</a></p>
</body>
</html>"""
    
    def app_debug_network(request):
        """Debug network functionality"""
        return """<!DOCTYPE html>
<html>
<head><title>Network Debug</title></head>
<body>
<h1>Network Debug - Simplified</h1>
<p>The system now uses <strong>picow.local</strong> as the default hostname.</p>
<p>Network diagnostics have been simplified for better reliability.</p>
<p><a href="/">Back to Home</a></p>
</body>
</html>"""
            
    def app_debug_hostname(request):
        """Check current hostname settings"""
        try:
            import network
            wlan = network.WLAN(network.STA_IF)
            
            # Get current network info
            if wlan.isconnected():
                ip, subnet, gateway, dns = wlan.ifconfig()
                
                # Try to get hostname if possible
                try:
                    # Some MicroPython versions expose hostname
                    hostname = wlan.config('hostname')
                    hostname_msg = f"Current hostname: {hostname}"
                except:
                    hostname_msg = "Hostname not accessible via config"
                
                result = f"""<!DOCTYPE html>
<html>
<head><title>Hostname Debug</title></head>
<body>
<h1>Hostname Debug Information</h1>
<p><strong>IP Address:</strong> {ip}</p>
<p><strong>{hostname_msg}</strong></p>
<p><strong>Test URLs:</strong></p>
                <ul>
                <li><a href="http://picow.local">http://picow.local</a></li>
                <li><a href="http://{ip}">http://{ip}</a> (direct IP)</li>
                </ul>
<p><strong>mDNS Status:</strong> Check which URLs work above</p>
<p><a href="/">Back to Home</a></p>
</body>
</html>"""
                return result
            else:
                return "WiFi not connected"
                
        except Exception as e:
            return f"Hostname debug error: {e}"
    
    def app_debug_lwip(request):
        """Test lwIP built-in mDNS functionality"""
        return """<!DOCTYPE html>
<html>
<head><title>lwIP Test</title></head>
<body>
<h1>lwIP Test - Simplified</h1>
<p>The system now uses default <strong>picow.local</strong> hostname.</p>
<p>Try accessing: <a href="http://picow.local">http://picow.local</a></p>
<p><a href="/">Back to Home</a></p>
</body>
</html>"""
            
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
        try:
            print(f"DEBUG: Serving index page from {APP_TEMPLATE_PATH}/index.html")
            return render_template(f"{APP_TEMPLATE_PATH}/index.html")
        except Exception as e:
            print(f"ERROR: Failed to render index template: {e}")
            return f"Template error: {e}"

    def app_toggle_led(request):
        onboard_led.toggle()
        return "OK"

    def app_catch_all(request):
        # For any unmatched route, serve the main page (DNS catchall behavior)
        try:
            print(f"DEBUG: Catch-all serving index for: {request.path}")
            return render_template(f"{APP_TEMPLATE_PATH}/index.html")
        except Exception as e:
            print(f"ERROR: Catch-all template error: {e}")
            return f"Catch-all template error: {e}"

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
    server.add_route("/debug_mdns", handler=app_debug_mdns, methods=["GET"])
    server.add_route("/debug_network", handler=app_debug_network, methods=["GET"])
    server.add_route("/debug_lwip", handler=app_debug_lwip, methods=["GET"])
    server.add_route("/debug_hostname", handler=app_debug_hostname, methods=["GET"])
    # Add other routes for your application...
    server.set_callback(app_catch_all)
    
    print("Application mode routes configured")


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
            print(f"WiFi connection attempt {wifi_current_attempt}/{WIFI_MAX_ATTEMPTS}")
            ip_address = connect_to_wifi(
                wifi_credentials["ssid"], wifi_credentials["password"]
            )

            if is_connected_to_wifi():
                print(f"Connected to wifi, IP address {ip_address}")
                # Add small delay to let CYW43 stabilize
                utime.sleep(3)
                break
            else:
                wifi_current_attempt += 1
                # Add delay between connection attempts for CYW43 stability
                if wifi_current_attempt < WIFI_MAX_ATTEMPTS:
                    utime.sleep(5)

        if is_connected_to_wifi():
            print("Starting application mode...")
            
            application_mode()
            # Note: Don't call server.run() here - it's called at the bottom
        else:
            # Bad configuration, delete the credentials file, reboot
            # into setup mode to get new credentials from the user.
            print("Bad wifi connection!")
            print("This might be due to CYW43 WiFi chip issues")
            print(wifi_credentials)
            os.remove(WIFI_FILE)
            machine_reset()

except Exception:
    # Either no wifi configuration file found, or something went wrong,
    # so go into setup mode.
    setup_mode()

# Start the web server...
print("Starting web server...")
try:
    server.run()
finally:
    print("Server stopped")
