[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ) [![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=social&logo=instagram&logoColor=black)](https://www.instagram.com/v_e_e_b/)

# Twirly Shirley

A remote-controlled, programmable turntable powered by USB-C. Useful for making stop motion video and generally rotating stuff that you can't (or are too lazy to) get to. 

There are relatively cheap turntables (only slightly more expensive than this DIY version) that do the same thing, but building one is more interesting/ flexible. For example, if you need to make a version for heavy weights/large items, the contents of this repository should be a good start, as well as a much cheaper option than [that kind of turntable](https://noxon.tech/en/360-turntable/).


# Hardware
- [Stepper Motor](https://www.amazon.de/TEQStone-Stepper-Printer-Degrees-Extruder/dp/B0BMX62X22/ref=sr_1_4)
- DRV8825 to control the stepper motor
- 20V PD trigger to power the turntable
- [Raspberry Pi Pico W](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html) 
- [Rotating Bearing](https://www.amazon.de/-/en/dp/B073NZ4GT4?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- [3d printed gears and case](3d/)

Total cost of materials: <50 USD

Build time: <2 hours (not including 3d printing time)

## Assembly

- Print the case and remove the supports if you've used any (for the USB port).

### Wiring



That's pretty much it. You can test that the components are working and then connect the gears to the bearing and assemble them in an enclosure. This is the bit where you can get creative. There are some files that you might find useful in the [3d directory](3d/).

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
```
(*NB. make sure you are using the right port name, as shown in the port listing command above*)

Done! All the required files should now be on the Pico. Whenever you connect to power the script will autorun.

# Controls
<img src="images/remote.png" width="33%">

- The > and < buttons give a **small nudge** clockwise or counterclockwise respectively.
- There is a **full circle spin** either clockwise or anticlockwise. 

# Video  

An overview of the build and a demo of it in action:

# Acknowledgements

The gears are made using the [openscad library by Chris Spencer](https://github.com/chrisspen/gears). 

The micropython driver for the drv8825 is by [Rob Hammerlin](https://gitlab.com/robhamerling/micropython-drv8825).

# Licence 

GPL 3.0
