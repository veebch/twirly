[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/v_e_e_b/)


# Twirly

A Infrared (IR) remote-controlled turntable. Useful for rotating stuff that you (can't/ are too lazy to) get to. You can pick up relatively cheap turntables (similar to the cost of this DIY version) that do the same thing, but building one is more interesting/ flexible. For example, if you need to make a high-weight version, this should be a good start.

There is ramping (gradually speeding up and slowing down) to avoid the side-effects of a sudden stop/start (things falling over etc).

The parts list below is just what we used, variations based on what you have lying around/ what's available should be easy to implement. 

# Hardware

- [IR receiver and Remote Control](https://www.amazon.de/-/en/DollaTek-Infrared-Wireless-Control-Arduino/dp/B07DJ58XGC)
- [DC Motor (12V)](https://www.amazon.de/gp/product/B0824V7YGT)
- [DC driver module](https://www.waveshare.com/pico-motor-driver.htm)
- 12V DC Power Supply
- Raspberry Pi Pico (No need for a W unless you plan to use WiFi)
- [Rotating Bearing](https://www.amazon.de/-/en/dp/B073NZ4GT4?psc=1&ref=ppx_yo2ov_dt_b_product_details)
- [Gears and Case](3d/)

# Assembly
Clone this repository, install ampy, and copy the required files to the pico.

Then
- Mount the pico to the DC motor driver board. 
- Connect the power to the driver board (this also powers the pico).
- Connect the motor to outputs **A1** and **A2** on the driver board.
- Connect the IR sensor, using **GPIO 0** for **VCC**, and **GPIO 16** for **S** (signal).

That's pretty much it. You can test that the components are working and then connect the gears to the bearing and assemble them in an enclosure. This is the bit where you can get creative. There are some files that you might find useful in the [3d directory](3d/).

# Video  


# Acknowledgements

IR code based on some of [Peter Hinch's work](https://github.com/peterhinch/micropython_ir). If you want to adapt the code to use a different remote, his repository has all the instructions on how to do so.
