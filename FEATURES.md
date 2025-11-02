# Features Guide

This guide details all the features and configuration options available in the turntable controller.

## Motor Control Features

### Microstepping Control

The system supports variable microstepping resolution for smooth motion control:

| Microsteps | Resolution | Description |
|------------|------------|-------------|
| 1 (full) | 1.8°/step | Maximum torque, fastest movement |
| 2 (half) | 0.9°/step | Good balance of speed and smoothness |
| 4 (quarter) | 0.45°/step | Smoother than half-step |
| 8 (eighth) | 0.225°/step | Very smooth operation |
| 16 | 0.1125°/step | Ultra-smooth, recommended default |
| 32 | 0.05625°/step | Maximum smoothness, slower movement |

**Configuration**: Set via web interface or modify `MICROSTEPS` in `main.py`

### Speed Ramping

3-phase acceleration/deceleration system for smooth starts and stops:

1. **Acceleration Phase**: Gradually increases from start speed to target speed
2. **Constant Speed Phase**: Maintains target speed for majority of movement
3. **Deceleration Phase**: Gradually decreases to stop speed

**Benefits**:
- Prevents motor stalling on startup
- Reduces mechanical stress
- Eliminates abrupt stops
- Smoother operation for photography/videography

### Gear Ratio Compensation

Automatic adjustment for mechanical gear reduction systems:

**Default Configuration**:
- Motor gear: 20 teeth
- Turntable gear: 81 teeth  
- Gear ratio: 4.05:1

**Customization**: Modify `GEAR_RATIO` in `main.py`:
```python
GEAR_RATIO = large_gear_teeth / small_gear_teeth
```

**Effects**:
- All rotation commands automatically compensated
- Maintains accurate angular positioning
- 360° rotation produces exactly one turntable revolution

### Direction Control

- **Clockwise**: Positive rotation values
- **Counter-clockwise**: Negative rotation values
- **Automatic**: Direction determined by rotation angle

## Web Interface Features

### Responsive Design

- **Desktop Optimized**: Full-featured interface with large controls
- **Mobile Friendly**: Touch-optimized buttons and responsive layout
- **Cross-Browser**: Compatible with modern browsers

### Dark Mode

Complete theming system with automatic preference saving:

**Features**:
- Toggle between light and dark themes
- Automatic preference persistence using localStorage
- Optimized for low-light environments
- Professional appearance for studio use

**Controls**:
- Click moon/sun icon to toggle
- Preference remembered across browser sessions
- Instant theme switching without page reload

### Real-time Control

**Manual Controls**:
- Step-by-step movement (1° increments)
- Quick rotation presets (90°, 180°, 270°, 360°)
- Direction control (CW/CCW)
- Emergency stop functionality

**Live Updates**:
- Current position display
- Motor status indicators
- Network connectivity status
- Real-time feedback on all operations

### Timelapse Mode

Automated rotation system for time-lapse photography:

**Parameters**:
- **Total Rotation**: 360° (full rotation) or custom angle
- **Number of Steps**: Configurable step count for desired frame rate
- **Delay Between Steps**: Pause time for camera exposure
- **Direction**: Clockwise or counter-clockwise

**Progress Tracking**:
- Real-time step counter (Step X of Y)
- Estimated time remaining
- Visual progress indicators
- Abort capability at any time

**Use Cases**:
- Product photography turntables
- 360° object documentation
- Time-lapse videos with rotation
- Automated scanning applications

## Network Features

### WiFi Connectivity

**Primary Mode**: Connects to existing WiFi network
- Automatic connection on startup
- DHCP IP assignment
- Status LED indication

**Configuration**: Edit WiFi credentials in `main.py`:
```python
WIFI_SSID = "your_network_name"
WIFI_PASSWORD = "your_password"
```

### Access Point Fallback

**Backup Mode**: Creates standalone network when WiFi unavailable
- Network name: "Twirly"
- IP address: 192.168.4.1
- No password required
- Automatic activation on WiFi failure

### mDNS Support

**Easy Access**: Device accessible via friendly name
- URL: `http://twirly.local`
- No need to remember IP addresses
- Automatic discovery on local network
- Compatible with most modern devices

## Status Indicators

### Activity LED

Visual feedback system using onboard LED:

**Network Status**:
- **Solid ON**: Connected to WiFi
- **Slow Blink**: Access Point mode active
- **Fast Blink**: Network connection attempt

**Motor Activity**:
- **Brief Flash**: Step command executed
- **Longer Flash**: Multi-step operation
- **Duration**: Configurable via `LED_DURATION_MS`

## Configuration Options

### Motor Parameters

Located in `main.py`, easily customizable:

```python
# Microstepping configuration
MICROSTEPS = 16          # Default microstepping resolution

# Gear system
GEAR_RATIO = 81/20       # Mechanical gear reduction

# Speed settings
MAX_SPEED = 2000         # Maximum steps per second
START_SPEED = 200        # Initial ramp speed
ACCELERATION = 1000      # Steps/second² acceleration

# LED behavior  
LED_DURATION_MS = 100    # Activity flash duration
```

### Network Settings

```python
# WiFi configuration
WIFI_SSID = "your_network"
WIFI_PASSWORD = "your_password"

# Access point fallback
AP_SSID = "Twirly"
AP_PASSWORD = None       # Open network
```

### Hardware Pins

All pin assignments configurable in `drv8825_setup.py`:

```python
# Motor control pins
STEP_PIN = 2
DIR_PIN = 3  
ENABLE_PIN = 4

# Microstepping pins
M0_PIN = 6
M1_PIN = 7
M2_PIN = 8
```

## Advanced Features

### Position Tracking

- Maintains current angular position
- Accurate step counting with microstepping
- Position reset capability
- Overflow protection for continuous operation

### Error Handling

- Network timeout protection
- Motor fault detection
- Graceful degradation on errors
- Automatic recovery mechanisms

### Performance Optimization

- Efficient step timing for DRV8825 compatibility
- Minimal latency web responses
- Optimized ramp calculations
- Memory-efficient operation on microcontroller

## Extensibility

The modular design allows easy customization:

**Hardware Extensions**:
- Additional sensors (limit switches, encoders)
- Different motor drivers
- External control interfaces

**Software Modifications**:
- Custom web interface themes
- Additional movement patterns
- Integration with external systems
- Custom API endpoints

**Communication Options**:
- Serial control interface
- MQTT integration potential
- REST API expansion
- WebSocket real-time updates