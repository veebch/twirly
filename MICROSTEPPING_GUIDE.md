# Microstepping Enhancement Guide

## Overview

This turntable project has been enhanced to use **microstepping** with **intelligent speed ramping** for smoother, more precise motor control. Microstepping divides each full step of the stepper motor into smaller increments, while speed ramping provides smooth acceleration and deceleration curves.

## Key Features

### Microstepping Benefits:
- **Smoother motion** with reduced vibration
- **Higher precision** positioning
- **Quieter operation**
- **Better low-speed performance**

### Speed Ramping Benefits:
- **Gentle acceleration/deceleration** prevents mechanical stress
- **Eliminates jerky starts/stops**
- **Reduces lost steps** at high speeds
- **Professional-quality motion** for photography/videography

## Microstepping Options

The DRV8825 driver supports the following microstepping resolutions:

| Microsteps | Resolution | Use Case | Ramping Applied |
|------------|------------|----------|-----------------|
| 1 | Full step | Maximum speed, basic positioning | Large moves only |
| 2 | Half step | Good balance of speed and smoothness | Large moves only |
| 4 | Quarter step | Better smoothness | Large moves only |
| 8 | 1/8 step | High precision applications | Most moves |
| 16 | 1/16 step | **Default** - Excellent smoothness | All large moves |
| 32 | 1/32 step | Maximum smoothness, slower speed | All moves |

## Speed Ramping Implementation

### When Ramping is Applied:
- ✅ **360° rotations**: Full ramping for smooth professional motion
- ✅ **Timelapse sequences**: Ramping on each movement for cinematic quality
- ✅ **Large movements**: Movements > 20 full steps equivalent
- ❌ **Small nudges**: No ramping for precise positioning
- ❌ **Tiny adjustments**: Movements < 6 full steps equivalent

### Ramping Profile:
1. **Acceleration Phase**: 15% of movement at 30-100% target speed
2. **Constant Phase**: 70% of movement at target speed
3. **Deceleration Phase**: 15% of movement at 100-30% target speed

## Web Interface Controls

### Basic Motor Controls
- **< and >**: Small nudge movements
- **◯ > and < ◯**: Full 360° rotations  
- **Title**: Timelapse sequence with ramping
- **Center button**: Emergency stop

### Microstepping Settings
- **Settings panel**: Choose from 1, 2, 4, 8, 16, or 32 microsteps
- **Status display**: Shows current microstepping configuration
- **Real-time switching**: Change settings without restarting

## API Endpoints

### Movement Controls
- `GET /cw_360` - Clockwise 360° rotation **with ramping**
- `GET /ccw_360` - Counter-clockwise 360° rotation **with ramping**
- `GET /cw_a_bit` - Small clockwise nudge **without ramping**
- `GET /ccw_a_bit` - Small counter-clockwise nudge **without ramping**
- `GET /timelapse` - Execute timelapse sequence **with ramping**
- `GET /stop` - Emergency stop

### Configuration & Testing
- `GET /microsteps?microsteps=<value>` - Set microstepping (1,2,4,8,16,32)
- `GET /microsteps` - Get current microstepping setting
- `GET /status` - Get system status including microstepping and ramping info
- `GET /test_ramping` - **NEW**: Test ramping functionality with controlled sequence

## Technical Implementation

### Speed Optimization with Ramping
The system automatically adjusts speeds and applies ramping based on microstepping resolution:

```python
# Speed scaling based on microstepping
speed = base_speed * (current_microsteps // 4)

# Intelligent ramping decision
if movement_size > microsteps * 20:
    action(steps, microsteps, speed, use_ramping=True)
else:
    action(steps, microsteps, speed, use_ramping=False)
```

### Ramping Algorithm
```python
# Three-phase movement for large motions:
# 1. Acceleration: 30% → 100% of target speed
# 2. Constant: 100% of target speed  
# 3. Deceleration: 100% → 30% of target speed
```

### Step Calculation
Physical movements are maintained by scaling step counts:

```python
# Same physical movement regardless of microstepping
steps = full_steps * current_microsteps
```

### Hardware Connections (Raspberry Pi Pico W)
- M0 pin: GPIO 12
- M1 pin: GPIO 11  
- M2 pin: GPIO 10
- STEP pin: GPIO 7
- DIR pin: GPIO 6
- SLEEP pin: GPIO 8
- RESET pin: GPIO 9

## Usage Examples

### Changing Microstepping via Web Interface
1. Open the turntable web interface
2. Use the microstepping buttons (1, 2, 4, 8, 16, 32)
3. Current setting is highlighted in orange
4. All subsequent movements use the new setting

### Changing Microstepping via API
```bash
# Set to 16 microsteps for smooth operation
curl "http://[pico-ip]/microsteps?microsteps=16"

# Set to 1 microstep for maximum speed
curl "http://[pico-ip]/microsteps?microsteps=1"

# Check current setting
curl "http://[pico-ip]/status"
```

### Testing Speed Ramping via API
```bash
# Test the ramping functionality
curl "http://[pico-ip]/test_ramping"

# Check system status (includes ramping info)
curl "http://[pico-ip]/status"
```

### Code Example with Ramping
```python
# Large movement with automatic ramping
action(steps=810 * 16, microsteps=16, speed=400, use_ramping=True)

# Small precise movement without ramping  
action(steps=6 * 8, microsteps=8, speed=200, use_ramping=False)

# Let system decide based on movement size
action(steps=100 * 16, microsteps=16, speed=300)  # Auto-ramping
```

## Recommendations

### For Different Use Cases:

**Photography/Videography**: Use 16 or 32 microsteps with ramping enabled for smooth, professional motion that eliminates camera shake

**Product Scanning**: Use 8 or 16 microsteps with ramping for good precision and smooth movement between positions

**Quick Positioning**: Use 1 or 2 microsteps - ramping automatically disabled for small moves, enabled for large moves

**Precision Work**: Use 16 or 32 microsteps with ramping for fine adjustments without vibration

### Performance Notes:
- **Ramping automatically applied** to movements > 20 full-step equivalent
- **Small nudges skip ramping** for immediate precise positioning  
- **Emergency stop works immediately** regardless of ramping state
- **Speed scaling optimized** for each microstepping level
- **Three-phase ramping** provides professional motion quality

### Motion Quality Comparison:
- **Without ramping**: Instant start/stop, possible vibration, good for tiny adjustments
- **With ramping**: Smooth acceleration/deceleration, professional quality, ideal for visible movements

## Troubleshooting

### Motor Not Moving
1. Check microstepping setting (try setting to 1 for testing)
2. Verify power supply (20V for motor, 5V for logic)
3. Check wiring connections
4. Test with lower speeds

### Jerky Movement
1. Increase microstepping (try 16 or 32)
2. Reduce speed if too high for current microstepping
3. Check for loose mechanical connections

### Web Interface Issues
1. Refresh page to reload current status
2. Check network connection to Pico W
3. Verify Pico W is running the updated firmware

## Testing

Run the test script to validate microstepping functionality:

```bash
# On the Pico W (via terminal/IDE)
python test_microstepping.py
```

This will test all microstepping configurations and validate the system is working correctly.