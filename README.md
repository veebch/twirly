![Action Shot](/images/thumb.jpg)

[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ) [![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=social&logo=instagram&logoColor=black)](https://www.instagram.com/v_e_e_b/)

# Twirly - WiFi Turntable Controller

A web-controlled turntable system using Raspberry Pi Pico W and DRV8825 stepper motor driver. Perfect for product photography, 360° documentation, and time-lapse videos.

## Quick Start

1. **Flash MicroPython** to your Pico W
2. **Wire the hardware** - see [WIRING.md](WIRING.md) for detailed connections
3. **Copy files** to the Pico W filesystem
4. **Edit WiFi settings** in `main.py`
5. **Access** the web interface at `http://twirly.local`

## Key Features

- **Microstepping Control**: Smooth motion with 1-32 microstepping
- **Web Interface**: Mobile-friendly with dark mode
- **Timelapse Mode**: Automated rotation for photography
- **Network Access**: WiFi with mDNS (`twirly.local`) or AP fallback

## Documentation

| Guide | Description |
|-------|-------------|
| [WIRING.md](WIRING.md) | Hardware connections and setup |
| [FEATURES.md](FEATURES.md) | Complete feature list and configuration |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
