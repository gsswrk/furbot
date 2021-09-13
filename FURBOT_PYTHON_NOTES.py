#!/usr/bin/env python3

# LCD DISPLAY
from aiy.voice.audio import AudioFormat, play_wav, record_file
import traceback
import tempfile
import os
import atexit
import time
import neopixel
import board
from aiy.board import Board, Led
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from time import sleep

serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)

# Box and text rendered in portrait mode
with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((10, 40), "Hello World", fill="white")

# BACK BUTTON


def main():
    print('LED is ON while button is pressed (Ctrl-C for exit).')
    with Board() as board:
        while True:
            board.button.wait_for_press()
            print('ON')
            board.led.state = Led.ON
            board.button.wait_for_release()
            print('OFF')
            board.led.state = Led.OFF


if __name__ == '__main__':
    main()


# LED EYES

#!/usr/bin/env python3


def exit_handler():
    pixels.fill((0, 0, 0))
    pixels.show()


atexit.register(exit_handler)

pixel_pin = board.D12
num_pixels = 2

ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    board.D12, 2, brightness=0.5, auto_write=False, pixel_order=ORDER
)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
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
    # while True:
    #        pixels = neopixel.NeoPixel(board.D12, 1) # Raspberry Pi wiring!
    #    pixels = neopixel.NeoPixel(board.D12, 1, brightness=0.5)
    #        pixels = (255, 0, 0)
    #        pixels[0] = (255, 255, 255)
    #        time.sleep(2)
    #        pixels[0] = (0, 0, 0)
    #        time.sleep(2)
    #        pixels[0] = (0, 255, 255)
    #        time.sleep(2)
    #        pixels[0] = (255, 0, 255)
    #        time.sleep(2)
    #        pixels[0] = (255, 255, 0)
    #        time.sleep(2)
    #        pixels[0] = (0, 0, 0)
    #        time.sleep(2)
    #        pixels.show()
    while True:
        # Comment this line out if you have RGBW/GRBW NeoPixels
        #        pixels.fill((255, 0, 0))
        # Uncomment this line if you have RGBW/GRBW NeoPixels
        # pixels.fill((255, 0, 0, 0))
        #        pixels.show()
        #        time.sleep(1)

        # Comment this line out if you have RGBW/GRBW NeoPixels
        #        pixels.fill((0, 255, 0))
        # Uncomment this line if you have RGBW/GRBW NeoPixels
        # pixels.fill((0, 255, 0, 0))
        #        pixels.show()
        #        time.sleep(1)

        # Comment this line out if you have RGBW/GRBW NeoPixels
        #        pixels.fill((0, 0, 255))
        # Uncomment this line if you have RGBW/GRBW NeoPixels
        # pixels.fill((0, 0, 255, 0))
        #        pixels.show()
        #        time.sleep(1)

        rainbow_cycle(0.01)  # rainbow cycle with 1ms delay per step
#        time.sleep(wait)


if __name__ == '__main__':
    main()

# VOICE RECOG

#!/usr/bin/env python3
#
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Checks that the AIY sound card is working."""


AIY_CARDS = {
    'sndrpigooglevoi': 'Voice HAT (v1)',
    'aiyvoicebonnet': 'Voice Bonnet (v2)'
}

TEST_SOUND_PATH = '/usr/share/sounds/alsa/Front_Center.wav'

RECORD_DURATION_SECONDS = 3

ERROR_NO_SOUND_CARDS = '''
You do not have any sound cards installed. Please check that AIY sound card is
properly connected.

For some Voice HATs (not Voice Bonnets!) you need to add the following line
to /boot/config.txt:

dtoverlay=googlevoicehat-soundcard

To do that simply run from a separate terminal:

echo "dtoverlay=googlevoicehat-soundcard" | sudo tee -a /boot/config.txt

'''

ERROR_NO_AIY_SOUND_CARDS = '''
You have sound cards installed but you do not have any AIY ones. Please check
that AIY sound card is properly connected.
'''

ERROR_NOT_A_FIRST_SOUND_CARD = '''
Your AIY sound card is not a first sound device. The voice recognizer may be
unable to find it. Please try removing other sound drivers.
'''

ERROR_NO_SPEAKER_SOUND = '''
There may be a problem with your speaker. Check that it is connected properly.
'''

ERROR_NO_RECORDED_SOUND = '''
There may be a problem with your microphone. Check that it is connected
properly.
'''


def ask(prompt):
    answer = input('%s (y/n) ' % prompt).lower()
    while answer not in ('y', 'n'):
        answer = input('Please enter y or n: ')
    return answer == 'y'


def error(message):
    print(message.strip())


def find_sound_cards(max_count=16):
    cards = []
    for i in range(max_count):
        path = '/proc/asound/card%d/id' % i
        if not os.path.exists(path):
            break
        with open(path) as f:
            cards.append(f.read().strip())
    return cards


def check_sound_card_present():
    cards = find_sound_cards()
    if not cards:
        error(ERROR_NO_SOUND_CARDS)
        return False

    aiy_cards = set.intersection(set(cards), AIY_CARDS.keys())
    if len(aiy_cards) != 1:
        error(ERROR_NO_AIY_SOUND_CARDS)
        return False

    for card in aiy_cards:
        index = cards.index(card)
        print('You have %s installed at index %d!' % (AIY_CARDS[card], index))
        if index != 0:
            error(ERROR_NOT_A_FIRST_SOUND_CARD)
            return False

    return True


def check_speaker_works():
    print('Playing a test sound...')
    play_wav(TEST_SOUND_PATH)

    if not ask('Did you hear the test sound?'):
        error(ERROR_NO_SPEAKER_SOUND)
        return False

    return True


def check_microphone_works():
    with tempfile.NamedTemporaryFile() as f:
        input('When you are ready, press Enter and say "Testing, 1 2 3"...')
        print('Recording for %d seconds...' % RECORD_DURATION_SECONDS)

        record_file(AudioFormat.CD, filename=f.name, filetype='wav',
                    wait=lambda: time.sleep(RECORD_DURATION_SECONDS))
        print('Playing back recorded audio...')
        play_wav(f.name)

    if not ask('Did you hear your own voice?'):
        error(ERROR_NO_RECORDED_SOUND)
        return False

    return True


def main():
    if not check_sound_card_present():
        return

    if not check_speaker_works():
        return

    if not check_microphone_works():
        return

    print('AIY sound card seems to be working!')


if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()
    finally:
        input('Press Enter to close...')
