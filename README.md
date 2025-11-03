![Action Shot](/images/thumb.jpg)

[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?style=flat&logo=youtube&logoColor=red&labelColor=white&color=ffed53)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ) [![GitHub](https://img.shields.io/github/stars/veebch?style=flat&logo=github&logoColor=black&labelColor=white&color=ffed53)](https://www.github.com/veebch)

# Twirly - WiFi Turntable Controller

A web-controlled turntable system using Raspberry Pi Pico W and DRV8825 stepper motor driver. Perfect for product photography, 360° documentation, and time-lapse videos.

## Demo Video

[![Twirly Demo Video](https://img.youtube.com/vi/peo0DxWtorY/0.jpg)](https://www.youtube.com/watch?v=peo0DxWtorY)

*Click to watch the full demonstration*

## Web Interface

![Remote Control Interface](/images/remote.png)

The mobile-friendly web interface provides complete control over the turntable with real-time feedback and dark mode support.

## Quick Start

1. **Flash MicroPython** to your Pico W
2. **Wire the hardware** - see [WIRING.md](WIRING.md) for detailed connections
3. **Copy files** to the Pico W filesystem
4. **Power on** - Twirly will automatically start an access point for WiFi setup
5. **Connect to "pi pico" WiFi** and configure your network credentials
6. **Access** the web interface at http://picow.local 

## Key Features

- **Microstepping Control**: Smooth motion with 1-32 microstepping
- **Web Interface**: Mobile-friendly with dark mode
- **Timelapse Mode**: Automated rotation for photography
- **Network Access**: WiFi with mDNS hostname (http://picow.local) and IP fallback

## Documentation

| Guide | Description |
|-------|-------------|
| [WIRING.md](WIRING.md) | Hardware connections and setup |
| [FEATURES.md](FEATURES.md) | Complete feature list and configuration |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.





