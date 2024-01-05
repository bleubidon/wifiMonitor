#!/usr/bin/env python3
from Hardware import Hardware
from time import sleep

Hardware.setupHardware()

while 1:
    print("On: {}; Toggle: {}".format(Hardware.getButtonStatus("off"), Hardware.getButtonStatus("toggle")))
    Hardware.setLed("all")
    sleep(.5)
    Hardware.setLed("off")
    sleep(.5)
