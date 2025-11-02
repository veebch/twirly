![Action Shot](/images/thumb.jpg)

[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ) [![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=social&logo=instagram&logoColor=black)](https://www.instagram.com/v_e_e_b/)

# Twirly - WiFi Turntable Controller

A web-controlled turntable system using Raspberry Pi Pico W and DRV8825 stepper motor driver. Perfect for product photography, 360° documentation, and time-lapse videos.

## Quick Start

### What You Need
- Raspberry Pi Pico W
- DRV8825 stepper motor driver  
- NEMA stepper motor (4-wire bipolar)
- 20V power supply for motor
- 5V power supply for logic

### Basic Setup

1. **Flash MicroPython** to your Pico W
2. **Wire the hardware** - see [WIRING.md](WIRING.md) for detailed connections
3. **Copy files** to the Pico W filesystem
4. **Edit WiFi settings** in `main.py`:
   ```python
   WIFI_SSID = "your_network_name"
   WIFI_PASSWORD = "your_password"
   ```
5. **Run** `main.py` on the Pico W
6. **Access** the web interface at `http://twirly.local`

## Key Features

- **Microstepping Control**: Smooth motion with 1-32 microstepping
- **Web Interface**: Mobile-friendly with dark mode
- **Timelapse Mode**: Automated rotation for photography
- **Network Access**: WiFi with mDNS (`twirly.local`) or AP fallback
- **Gear Compensation**: Automatic adjustment for gear ratios

## Documentation

| Guide | Description |
|-------|-------------|
| [WIRING.md](WIRING.md) | Detailed hardware connections and setup |
| [FEATURES.md](FEATURES.md) | Complete feature list and configuration options |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |

## Quick Hardware Setup

### Essential Connections
```
Pico W          DRV8825
------          -------
GP2       →     STEP
GP3       →     DIR  
GP4       →     ENABLE
GP6-8     →     M0-M2 (microstepping)
GND       →     GND

Power: 20V to VMOT, 5V to VDD
Motor: 4-wire stepper to 2B,2A,1A,1B
```

### Current Limiting
Set DRV8825 current limit before connecting motor:
1. Measure voltage on current limit potentiometer
2. Adjust to: `Motor_Current × 0.8` volts
3. Example: 1.5A motor = 1.2V reference

## Usage

1. **Power on** - device connects to WiFi or creates "Twirly" network
2. **Open browser** to `http://twirly.local` (or shown IP address)
3. **Control manually** with step buttons or rotation presets
4. **Run timelapse** with custom parameters and progress tracking

## File Structure

- `main.py` - Main web server and motor control
- `drv8825.py` - Stepper motor driver with proper timing
- `drv8825_setup.py` - Microstepping pin configuration  
- `app_templates/` - Web interface files
- `phew/` - Lightweight web framework

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
- Step-down converter Ground → DRV8825 GND (logic ground)
- Step-down converter 5V output → Pico VSYS
- Step-down converter Ground → Pico GND

#### DRV8825 to Raspberry Pi Pico W Connections

**Essential Control Pins:**
- Pico GPIO 6 → DRV8825 DIR (Direction control)
- Pico GPIO 7 → DRV8825 STEP (Step pulse input)
- Pico GPIO 8 → DRV8825 SLEEP (Must be HIGH to enable driver)
- Pico GPIO 9 → DRV8825 RESET (Must be HIGH for normal operation)
- Pico GND → DRV8825 GND (logic ground)

**Microstepping Control Pins (M0, M1, M2):**
- Pico GPIO 12 → DRV8825 M0
- Pico GPIO 11 → DRV8825 M1
- Pico GPIO 10 → DRV8825 M2

**Enable Pin Configuration:**
- DRV8825 ENABLE → GND (always enabled for continuous operation)

#### DRV8825 to Stepper Motor Connections

**4-Wire Bipolar Stepper Motor:**
The stepper motor has two coils (A and B), each with two wires. Connect as follows:
- Motor Coil A Wire 1 → DRV8825 A1
- Motor Coil A Wire 2 → DRV8825 A2
- Motor Coil B Wire 1 → DRV8825 B1
- Motor Coil B Wire 2 → DRV8825 B2

**Important:** All four motor wires must be connected. The motor will not function properly with only partial connections. If the motor direction is incorrect, swap the connections of one coil (either A1/A2 or B1/B2).

#### Microstepping Resolution Control

The M0, M1, M2 pins control the stepping resolution according to this table:

| M2 | M1 | M0 | Resolution | Steps per Revolution |
|----|----|----|------------|---------------------|
| 0  | 0  | 0  | Full step  | 200                 |
| 0  | 0  | 1  | Half step  | 400                 |
| 0  | 1  | 0  | 1/4 step   | 800                 |
| 0  | 1  | 1  | 1/8 step   | 1600                |
| 1  | 0  | 0  | 1/16 step  | 3200                |
| 1  | 0  | 1  | 1/32 step  | 6400                |

The default configuration uses 1/16 microstepping (16 microsteps per full step) for smooth operation.

#### Current Limiting

The DRV8825 includes a potentiometer for current limiting. Set this according to your stepper motor specifications:
- Measure the reference voltage on the REF pin
- Current limit = VREF × 2
- For a 1A motor, set VREF to 0.5V
- Always set current limit at or below motor rating

#### Capacitor Placement

Install decoupling capacitors close to the DRV8825:
- 100μF electrolytic capacitor across 20V motor power (VMOT to GND)
- 100μF electrolytic capacitor across 5V logic power (VDD to GND)

These capacitors smooth voltage fluctuations and protect against voltage spikes.

The capacitors are connected across the voltage and ground rails on the yellow prototype card for the 20V and 5V supplies respectively (providing a smoother voltage for the bridge).

#### Gear Ratio Configuration

The turntable uses a gear reduction system where the stepper motor drives a small gear that rotates a larger turntable gear. The default configuration assumes:
- Motor gear: 20 teeth
- Turntable gear: 81 teeth
- Gear ratio: 4.05:1 (81/20)

This means the motor must rotate 4.05 times to achieve one full rotation of the turntable. The software automatically compensates for this ratio in all movement calculations.

To modify the gear ratio for different gear combinations, update the GEAR_RATIO constant in main.py:
```python
GEAR_RATIO = large_gear_teeth / small_gear_teeth
```

## Features

### Microstepping Control
The system supports variable microstepping resolution from 1 to 32 microsteps per full step, providing smooth motion control. Higher microstepping values result in smoother rotation but require more steps for the same angular movement.

### Web Interface
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode**: Toggle between light and dark themes with automatic preference saving
- **Real-time Control**: Instant motor control and status updates
- **Timelapse Mode**: Automated rotation with configurable parameters and progress tracking

### Network Access
- **mDNS Support**: Access the device at `twirly.local` without knowing the IP address
- **WiFi AP Mode**: Creates its own network when unable to connect to existing WiFi
- **Status LED**: Visual feedback for network connectivity and motor activity

### Motor Control
- **Speed Ramping**: 3-phase acceleration/deceleration for smooth starts and stops
- **Gear Ratio Compensation**: Automatic adjustment for mechanical gear reduction
- **Direction Control**: Clockwise and counter-clockwise rotation
- **Precise Positioning**: Accurate angular positioning with microstepping precision

## Troubleshooting

### Motor Not Moving
1. **Check Wiring**: Verify all four motor wires are properly connected to the DRV8825 outputs (2B, 2A, 1A, 1B)
2. **Power Supply**: Ensure the motor power supply (M+ and M-) is connected and providing adequate voltage
3. **Current Limiting**: Verify the DRV8825 current limit is properly set for your motor
4. **Enable Pin**: Confirm the ENABLE pin is properly connected and the motor is enabled in software

### Erratic Movement
1. **Timing Issues**: The DRV8825 requires minimum 1.9μs pulse width - ensure proper timing delays
2. **Power Supply Noise**: Add capacitors across power supply lines to reduce electrical noise
3. **Loose Connections**: Check all wire connections for secure contact
4. **Current Setting**: Adjust the DRV8825 current limit potentiometer if motor skips steps

### Network Issues
1. **WiFi Connection**: Check that WiFi credentials are correct in main.py
2. **mDNS Problems**: If `twirly.local` doesn't work, use the IP address displayed on startup
3. **Access Point Mode**: Device creates "Twirly" network if WiFi connection fails

### Web Interface Problems
1. **Browser Compatibility**: Use a modern browser with JavaScript enabled
2. **Network Connectivity**: Ensure device and browser are on the same network
3. **Cache Issues**: Hard refresh the page (Ctrl+F5) if updates don't appear 

<div align="center">
<img src="images/guts.jpg" width="66%">
</div>

That's pretty much it. You can test that the components are working and then connect the gears to the bearing and assemble them in an enclosure. There parts we used are in the [3d directory](3d/).

# Firmware

Download a `uf2` image and install it on the Pico according to the [instructions](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython) on the Raspberry Pi website.

Clone this repository to your computer using the commands (from a terminal):

```
cd ~
git clone https://github.com/veebch/twirly.git
cd twirly
```

Check the port of the pico with the port listing command:
```
python -m serial.tools.list_ports
```
Now, using the port path (in our case `/dev/ttyACM0`) copy the contents to the repository by installing [ampy](https://pypi.org/project/adafruit-ampy/) and using  and the commands:

```
ampy -p /dev/ttyACM0 put main.py
ampy -p /dev/ttyACM0 put phew
ampy -p /dev/ttyACM0 put ap_templates
ampy -p /dev/ttyACM0 put app_templates
ampy -p /dev/ttyACM0 put drv*
ampy -p /dev/ttyACM0 put encoder_portable.py
ampy -p /dev/ttyACM0 put switch.py
```
(*NB. make sure you are using the right port name, as shown in the port listing command above*)

Done! All the required files should now be on the Pico. Whenever you connect to power the script will autorun.

# Controls

First, give your WiFi credentials to the Pico by scanning for the WiFi and connecting to 'pi pico'. You'll be redirected to a webpage that asks for your WiFi credentials. 
Then, point a web browser at the IP of the Pico and you'll see:

<div align="center">
<img src="images/remote.png" width="33%">
</div>


(It is possible to do make a control page without connecting to a router, but giving the pico W an internet connection makes it easier to add features later.)

- The > and < buttons give a **small nudge** clockwise or counterclockwise respectively.
- There is a **full circle spin** either clockwise or anticlockwise. 

# Video  

An overview of the build and a demo of it in action:

[![YouTube](http://i.ytimg.com/vi/peo0DxWtorY/hqdefault.jpg)](https://www.youtube.com/watch?v=peo0DxWtorY)
# Lighting diagram for Roller-Boot Video

<div align="center">
<img src="images/lighting.png" width="66%">
</div>

# Acknowledgements

The gears are made using the [openscad library by Chris Spencer](https://github.com/chrisspen/gears). 

The micropython driver for the drv8825 is by [Rob Hammerlin](https://gitlab.com/robhamerling/micropython-drv8825).

The remote control was based on [Phewap by Simon Prickett](https://github.com/simonprickett/phewap)

# Licence 

GPL 3.0
