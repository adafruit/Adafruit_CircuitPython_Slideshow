# The MIT License (MIT)
#
# Copyright (c) 2018 Kattni Rembor for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
`adafruit_slideshow`
====================================================
CircuitPython helper library for displaying a slideshow of images on a board with a built-in
display.

* Author(s): Kattni Rembor, Carter Nelson

Implementation Notes
--------------------

**Hardware:**

 * `Adafruit Hollowing M0 Express <https://www.adafruit.com/product/3900>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""
import time
import os
import random
import board
import displayio
import pulseio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Slideshow.git"


class SlideShow():
    """Class for displaying a slideshow of .bmp images on boards with built-in
    displays.

    :param str folder: Specify the folder containing the image files, in quotes. Default is
                       the root directory, ``"/"``.

    :param order: The order in which the images display. You can choose random (``RANDOM``) or
                  alphabetical (``ALPHA``). Default is ``RANDOM``.

    :param loop: Specify whether to loop the images or play through the list once. `True`
                 if slideshow will continue to loop, ``False`` if it will play only once.
                 Default is ``True``.

    :param int dwell: The number of seconds each image displays, in seconds. Default is 3.

    Example code for Hollowing Express. With this example, the slideshow will play through once
    in alphabetical order:

    .. code-block:: python

        import adafruit_slideshow

        slideshow = adafruit_slideshow.SlideShow()
        slideshow.loop = False
        slideshow.order = slideshow.ALPHA

        while slideshow.update():
            pass
    """
    MAX_BRIGHTNESS = 2 ** 15

    ALPHA = 0
    RANDOM = 1

    FADE_IN = 0
    SHOW_IMG = 1
    FADE_OUT = 2
    LOAD_IMG = 3

    def __init__(self, folder="/", order=RANDOM, loop=True, dwell=3):
        self._group = displayio.Group()
        board.DISPLAY.show(self._group)
        self._backlight = pulseio.PWMOut(board.TFT_BACKLIGHT)
        self._folder = folder
        self._order = order
        self._loop = loop
        self._dwell = dwell
        self._current_state = self.LOAD_IMG
        self._img_start = None
        self._file_list = None
        self._images = None
        self._load_images()

    @property
    def folder(self):
        """Specifies the folder containing the image files. Default is the root directory, ``"/"``.
        """
        return self._folder

    @folder.setter
    def folder(self, folder):
        self._folder = folder

    @property
    def order(self):
        """Specifies the order in which the images are displayed. Options are random (``RANDOM``) or
        alphabetical (``ALPHA``). Default is ``RANDOM``."""
        return self._order

    @order.setter
    def order(self, order):
        self._order = order

    @property
    def loop(self):
        """Specifies whether to loop through the images continuously or play through the list once.
        ``True`` will continue to loop, ``False`` will play only once. Default is `True`."""
        return self._loop

    @loop.setter
    def loop(self, loop):
        self._loop = loop

    @property
    def dwell(self):
        """The number of seconds each image displays, in seconds. Default is 3."""
        return self._dwell

    @dwell.setter
    def dwell(self, dwell):
        self._dwell = dwell

    def update(self):
        """Updates the slideshow to the next image."""
        now = time.monotonic()
        if self._current_state == self.FADE_IN:
            steps = 100
            for b in range(steps):
                self._backlight.duty_cycle = b * SlideShow.MAX_BRIGHTNESS // steps
                time.sleep(0.01)
            self._current_state = self.SHOW_IMG
            self._img_start = time.monotonic()

        if self._current_state == self.SHOW_IMG:
            if now - self._img_start > self._dwell:
                self._current_state = self.FADE_OUT

        if self._current_state == self.FADE_OUT:
            steps = 100
            for b in range(steps, -1, -1):
                self._backlight.duty_cycle = b * SlideShow.MAX_BRIGHTNESS // steps
                time.sleep(0.01)
            self._group.pop()
            self._current_state = self.LOAD_IMG

        if self._current_state == self.LOAD_IMG:
            try:
                imagename = next(self._images)
            except StopIteration:
                return False
            try:
                self._show_bmp(imagename)
                self._current_state = self.FADE_IN
            except ValueError as error:
                print("Incompatible image:", imagename, str(error))

        return True

    def _show_bmp(self, imagename):
        """Opens and loads the image onto the display."""
        with open(imagename, "rb") as image:
            odb = displayio.OnDiskBitmap(image)
            face = displayio.Sprite(odb, pixel_shader=displayio.ColorConverter(), position=(0, 0))
            self._group.append(face)
            board.DISPLAY.wait_for_frame()

    def _get_next_image(self):
        """Cycles through the list of images."""
        while True:
            for image in self._file_list:
                yield image
            if not self._loop:
                return

    def _load_images(self):
        """Loads the list of images to be displayed in alphabetical or random order."""
        self._file_list = self._get_filenames()
        if self._order == SlideShow.RANDOM:
            self._file_list = sorted(self._file_list, key=lambda x: random.random())
            self._images = self._get_next_image()

    def _get_filenames(self, extension="bmp"):
        """Creates a list of available image files ending with .bmp in the specified folder."""
        return list(filter(lambda x: x.endswith(extension), os.listdir(self._folder)))
