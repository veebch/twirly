# Drivers Directory

This directory contains all the hardware driver files and technical documentation for the Twirly project.

## Core Files

- **`drv8825.py`** - Main DRV8825 stepper motor driver class
- **`drv8825_setup.py`** - Hardware initialization and configuration

## Test and Example Files

- **`drv8825_followme.py`** - Interactive control example
- **`drv8825_speeds.py`** - Speed testing utilities  
- **`drv8825_steps.py`** - Step counting examples
- **`drv8825_turns.py`** - Rotation testing
- **`test_microstepping.py`** - Microstepping validation

## Additional Hardware

- **`encoder_portable.py`** - Rotary encoder support
- **`switch.py`** - Switch/button utilities

## Documentation

- **`MICROSTEPPING_GUIDE.md`** - Technical guide to microstepping configuration

## Usage

These files are imported by the main application. The primary entry point is `drv8825_setup.py` which initializes the motor hardware.