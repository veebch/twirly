# Troubleshooting Guide

This guide helps diagnose and fix common issues with the turntable controller.

## Motor Issues

### Motor Not Moving

**Symptoms**: Motor doesn't rotate when commands are sent

**Causes and Solutions**:

1. **Wiring Problems** (Most Common)
   - **Check**: Verify all four motor wires are connected to DRV8825 outputs
   - **Fix**: Ensure secure connections to 2B, 2A, 1A, 1B terminals
   - **Note**: "It's always the wires" - this is the #1 cause of motor issues

2. **Power Supply Issues**
   - **Check**: Verify 20V motor supply is connected to VMOT and GND
   - **Check**: Verify 5V logic supply is connected to VDD and GND
   - **Fix**: Ensure power supplies are providing correct voltages

3. **Enable Pin Problem**
   - **Check**: ENABLE pin should be connected to GP4
   - **Check**: Motor should be enabled in software (ENABLE pin LOW)
   - **Fix**: Verify pin connection and software enable state

4. **Current Limit Too Low**
   - **Check**: Measure VREF voltage on DRV8825 potentiometer
   - **Fix**: Adjust current limit to appropriate level for your motor

### Erratic or Jerky Movement

**Symptoms**: Motor moves but skips steps, jerks, or moves inconsistently

**Causes and Solutions**:

1. **Timing Issues**
   - **Problem**: DRV8825 requires minimum 1.9μs pulse width
   - **Check**: Verify `drv8825.py` includes proper timing delays
   - **Fix**: Ensure `utime.sleep_us(2)` calls are present in step function

2. **Power Supply Noise**
   - **Problem**: Electrical noise affecting motor control
   - **Check**: Verify capacitors are installed (470µF on 20V, 100µF on 5V)
   - **Fix**: Add or replace power supply filtering capacitors

3. **Loose Connections**
   - **Check**: All wire connections for secure contact
   - **Fix**: Reseat all connections, especially power and motor wires

4. **Current Setting Issues**
   - **Problem**: Current limit too high or too low
   - **Check**: Motor temperature and movement quality
   - **Fix**: Adjust DRV8825 current limit potentiometer

### Motor Overheating

**Symptoms**: Motor or driver gets excessively hot

**Causes and Solutions**:

1. **Current Limit Too High**
   - **Check**: Measure VREF and calculate actual current limit
   - **Fix**: Reduce current limit to motor's rated current or below

2. **Continuous Operation**
   - **Problem**: Motor held in position with high current
   - **Fix**: Consider reducing hold current or using enable pin

3. **Poor Heat Dissipation**
   - **Fix**: Add heatsink to DRV8825 or improve airflow

## Network Issues

### Cannot Connect to WiFi

**Symptoms**: Device doesn't connect to your WiFi network

**Troubleshooting Steps**:

1. **Check Credentials**
   - **Verify**: WiFi name and password in `main.py` are correct
   - **Note**: WiFi names and passwords are case-sensitive

2. **Signal Strength**
   - **Check**: Device is within range of WiFi router
   - **Try**: Move closer to router during setup

3. **Network Compatibility**
   - **Check**: Router supports 2.4GHz (Pico W doesn't support 5GHz)
   - **Check**: No special characters in WiFi name or password

4. **Access Point Fallback**
   - **Solution**: Device creates "Twirly" network if WiFi fails
   - **Connect**: Join "Twirly" network and access via 192.168.4.1

### Cannot Access twirly.local

**Symptoms**: Browser can't find twirly.local address

**Troubleshooting Steps**:

1. **mDNS Support**
   - **Check**: Your device supports mDNS (most modern systems do)
   - **Alternative**: Use IP address instead (shown on device startup)

2. **Network Issues**
   - **Check**: Both device and computer are on same network
   - **Try**: Refresh/restart network connections

3. **Browser Problems**
   - **Try**: Different browser or incognito/private mode
   - **Clear**: Browser DNS cache

4. **Firewall/Security**
   - **Check**: Firewall isn't blocking mDNS traffic
   - **Try**: Temporarily disable firewall for testing

## Web Interface Issues

### Page Won't Load

**Symptoms**: Browser shows connection error or timeout

**Troubleshooting Steps**:

1. **Network Connectivity**
   - **Check**: Device and browser are on same network
   - **Try**: Ping the device IP address

2. **Device Status**
   - **Check**: Status LED shows network activity
   - **Try**: Reset device and wait for startup

3. **Browser Issues**
   - **Clear**: Browser cache and cookies
   - **Try**: Different browser or device

### Controls Don't Work

**Symptoms**: Web interface loads but buttons don't control motor

**Troubleshooting Steps**:

1. **JavaScript Issues**
   - **Check**: Browser has JavaScript enabled
   - **Check**: Browser console for error messages
   - **Try**: Hard refresh (Ctrl+F5)

2. **Network Latency**
   - **Check**: Network connection quality
   - **Try**: Wait longer for responses

3. **Device Overload**
   - **Check**: Only one user at a time
   - **Try**: Close other browser tabs/windows

## Hardware Debugging Process

When motor issues occur, follow this systematic approach:

### Step 1: Visual Inspection
- Check all wire connections
- Verify power LED indicators
- Look for loose or damaged components

### Step 2: Power Verification
- Measure 20V motor supply voltage
- Measure 5V logic supply voltage
- Check ground connections

### Step 3: Signal Testing
- Verify STEP pin pulses with oscilloscope/logic analyzer
- Check DIRECTION pin state changes
- Confirm ENABLE pin operation

### Step 4: Motor Testing
- Test motor with different current limits
- Try lower microstepping settings
- Verify motor specifications match driver capabilities

## Getting Help

If problems persist after following this guide:

1. **Check Documentation**: Review [WIRING.md](WIRING.md) and [FEATURES.md](FEATURES.md)
2. **Verify Setup**: Double-check all connections and settings
3. **Test Components**: Try with different motor or driver if available
4. **Report Issues**: Create GitHub issue with:
   - Detailed problem description
   - Hardware setup information
   - Steps already attempted
   - Any error messages or unusual behavior