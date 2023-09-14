[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/v_e_e_b/)


# Twirly Shirley

A Infrared (IR) remote-controlled turntable. Useful for rotating stuff that you (can't/ are too lazy to) get to. 

The application in the video is photography, but it could easily be repurposed as a rotating TV stand/ food carousel/ cake decorating robot etc.

There are relatively cheap turntables (only slightly more expensive than this DIY version) that do the same thing, but building one is more interesting/ flexible. For example, if you need to make a version for heavy weights/large items, this should be a good start, as well as a much cheaper option than [that kind of turntable](https://noxon.tech/en/360-turntable/).


# Hardware

- [IR receiver and Remote Control](https://www.amazon.de/-/en/DollaTek-Infrared-Wireless-Control-Arduino/dp/B07DJ58XGC)
- [DC Motor](https://www.amazon.de/gp/product/B0824V7YGT)
- [L298N H bridge](https://www.reichelt.com/ch/de/entwicklerboards-motorsteuerung-2-fach-l298n-debo-drv1-l298n-p282644.html?PROVID=2808) (will handle power/motors up to 35V)
- [Raspberry Pi Pico](https://www.pi-shop.ch/raspberry-pi-pico) (No need for a Pico **W** for current functionality. Although ou could use a W to make a turntable that's controlled by a webpage, which you might prefer to the IR remote control option)
- [Rotating Bearing](https://www.amazon.de/-/en/dp/B073NZ4GT4?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- [3d printed gears and case](3d/)

Total cost of materials: ~ 35 USD (power supply for motor not included)

Build time: <2 hours (not including 3d printing time)

## Assembly

- Connect a power source to **VCC** and **GND** on the h bridge.
- Connect **GPIO 14** and **GPIO 15** to **IN C** and **IN D** on the h bridge.
- Connect the motor to outputs **C** and **D** on the h bridge.
- Connect the IR sensor, using **GPIO 0** for **VCC**, and **GPIO 16** for **S** (signal).

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
ampy -p /dev/ttyACM0 put ir_rx
```
(*NB. make sure you are using the right port name, as shown in the port listing command above*)

Done! All the required files should now be on the Pico. Whenever you connect to power the script will autorun.

# Controls

- There is a **continuous spin** either clockwise or anticlockwise. When the motor is spinning, the left and right buttons control speed. 
- If the motor isn't spinning, the speed buttons give a **small nudge** clockwise or counterclockwise.
- There is also a button that performs **One (approx) 360 degree spin**  in 128 steps of 3 seconds for automated 360° photos.

All options other than nudges use speed ramping to lessen the chance of things falling over.

# Video  

A quick overview of the build and a demo of it in action.

# Acknowledgements

IR code based on some of [Peter Hinch's work](https://github.com/peterhinch/micropython_ir). If you want to adapt the code to use a different remote, the testing file in the `ir_tx` should help.

The gears are made using the [openscad library by Chris Spencer](https://github.com/chrisspen/gears).

# Licence 

GPL 3.0
