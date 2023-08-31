import os
import gc
import supervisor
import board
import microcontroller
import neopixel
import time

# import displayio
import terminalio
from digitalio import DigitalInOut, Direction, Pull
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# import adafruit_displayio_sh1106
from adafruit_apds9960.apds9960 import APDS9960


# --I2C-BUS
i2c = board.I2C()  # alternative i2c=busio.I2C(biard.SCL, board.SDA)

# --DISPLAY-SETUP
# displayio.release_displays() # <---- necessary for parallel i2c use
# display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
# display = adafruit_displayio_sh1106.SH1106(display_bus, width=132, height=64)

# --TIMER
last_time1 = time.monotonic()

# --STOR-STATS
# fs_stat = os.statvfs('/')
# print("|Disk: ", fs_stat[0] * fs_stat[2] / 1024 / 1024, " mb|")
# print("|Free: ", fs_stat[0] * fs_stat[3] / 1024 / 1024, " mb|")
# print("|==================|")

# --SENSOR
apds = APDS9960(i2c)  # address=0x39
apds.enable_proximity = True
apds.enable_gesture = True

# --BUTTON (BOOTSL)
switch = DigitalInOut(board.BUTTON)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

# --HID
mouse = Mouse(usb_hid.devices)
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)

# --NEOPIXEL-RAINBOW
try:
    from rainbowio import colorwheel
except:

    def colorwheel(pos):
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)


led = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)

print("| Neopxl--> active |")
time.sleep(0.05)
print("| HID-----> active |")
time.sleep(0.05)
print("| Sensor--> active |")
time.sleep(0.05)
# ===========================MAIN=LOOP=================================

while True:
    # ~rainbow
    led.fill(colorwheel((time.monotonic() * 50) % 255))
    time.sleep(0.005)

    # ~mouse (do something every x seconds without sleep)
    if time.monotonic() - last_time1 > 5.0:  # every 5 seconds
        last_time1 = time.monotonic()  # save when we do the thing
        # do the jiggle
        mouse.move(x=-2, y=1)
        time.sleep(0.05)
        mouse.move(x=-1, y=2)
        time.sleep(0.05)
        mouse.move(x=1, y=1)
        time.sleep(0.05)
        mouse.move(x=2, y=1)
        time.sleep(0.05)
        mouse.move(x=2, y=-1)
        time.sleep(0.05)
        mouse.move(x=1, y=-2)
        time.sleep(0.05)
        mouse.move(x=-1, y=-1)
        time.sleep(0.05)
        mouse.move(x=-2, y=-1)
    # endif

    # ~gesture-controll
    gesture = apds.gesture()
    if gesture == 0x01:  # -->to-YOU
        print("| ------^^^^------ |")
        time.sleep(0.1)
        kbd.send(40)  # Return/Enter
    elif gesture == 0x02:  # -->to-ME
        print("| ------vvvv------ |")
        kbd.send(227, Keycode.L)  # Win+L to lock screen
    elif gesture == 0x03:  # <--right-to-LEFT||
        print("| ------<<<<------ |")
        layout.write(os.getenv("MY_USER_NAME_FROM_SETTINGS-TOML"))
        # info: os.getenv() to get env-variables from settings.toml
        time.sleep(0.05)
        kbd.send(43)  # TAB
        time.sleep(0.05)
        layout.write(os.getenv("MY_PASSWORD_FROM_SETTINGS-TOML"))
        time.sleep(0.05)
        kbd.send(40)  # Return/Enter
    elif gesture == 0x04:  # ||left-to-RIGHT-->
        print("| ------>>>>------ |")
        layout.write(os.getenv("OTHER_STRING_FROM_SETTINGS-TOML"))
        time.sleep(0.05)
        kbd.send(40)  # Return/Enter

    # ~print RAM every x sec.
    #    if time.monotonic() - last_time1 > 7.5:
    #        last_time1 = time.monotonic() # save when we do the thing
    #        print( "| RAM: ",gc.mem_free() / 1024 * 1.000, " kb|" )
    # ~button
    if switch.value:
        # led.brightness = 0.1
        pass
    else:
        led.brightness = 0
        print("| Stealth-> active |")
