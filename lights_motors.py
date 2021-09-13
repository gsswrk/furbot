#!/usr/bin/env python3

import board
import neopixel
import atexit
from gpiozero import PWMOutputDevice
from time import sleep

motor = PWMOutputDevice(4)
pixel_pin = board.D12
num_pixels = 2
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    board.D12, 2, brightness=0.25, auto_write=False, pixel_order=ORDER
    )

def exit_handler():
    pixels.fill((0, 0, 0))
    pixels.show()

atexit.register(exit_handler)

def wheel(pos):
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)

def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def main():
    while True:
        rainbow_cycle(0.01)
        motor.on()
        motor.value = 0
        sleep(1)
        motor.value = .5
        sleep(1)
        motor.value = 1
        sleep(1)

if __name__ == '__main__':
    main()
