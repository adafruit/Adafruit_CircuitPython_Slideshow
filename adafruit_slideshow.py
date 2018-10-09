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

* Author(s): Kattni Rembor, Carter Nelson, Roy Hooper

Implementation Notes
--------------------

**Hardware:**

 * `Adafruit Hallowing M0 Express <https://www.adafruit.com/product/3900>`_

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


_FADE_IN = 0
_SHOW_IMG = 1
_FADE_OUT = 2
_LOAD_IMG = 3
_WAIT = 4


class PlayBackMode:
    """Helper class for handling playback mode."""
    # pylint: disable=too-few-public-methods
    ALPHA = 0
    RANDOM = 1
    # pylint: enable=too-few-public-methods


class PlayBackDirection:
    """Helper class for handling playback direction."""
    # pylint: disable=too-few-public-methods
    BACKWARD = -1
    FORWARD = 1
    # pylint: enable=too-few-public-methods


class SlideShow:
    # pylint: disable=too-many-instance-attributes
    """
    Class for displaying a slideshow of .bmp images on boards with built-in displays.

    :param str folder: Specify the folder containing the image files, in quotes. Default is
                       the root directory, ``"/"``.

    :param order: The order in which the images display. You can choose random (``RANDOM``) or
                  alphabetical (``ALPHA``). Default is ``RANDOM``.

    :param loop: Specify whether to loop the images or play through the list once. `True`
                 if slideshow will continue to loop, ``False`` if it will play only once.
                 Default is ``True``.

    :param int dwell: The number of seconds each image displays, in seconds. Default is 3.

    :param fade_effect: Specify whether to include the fade effect between images. ``True``
                        tells the code to fade the backlight up and down between image display
                        transitions. ``False`` maintains max brightness on the backlight between
                        image transitions. Default is ``True``.

    :param auto_advance: Specify whether to automatically advance after dwell seconds. ``True``
                 if slideshow should auto play, ``False`` if you want to control advancement
                 manually.  Default is ``True``.

    Example code for Hallowing Express. With this example, the slideshow will play through once
    in alphabetical order:

    .. code-block:: python

        import adafruit_slideshow

        slideshow = adafruit_slideshow.SlideShow()
        slideshow.loop = False
        slideshow.order = PlayBackMode.ALPHA

        while slideshow.update():
            pass

    Example code for Hallowing Express. Sets ``dwell`` to 0 seconds, turns ``auto_advance`` off,
    and uses capacitive touch to advance backwards and forwards through the images and to control
    the brightness level of the backlight:

    .. code-block:: python

        from adafruit_slideshow import PlayBackMode, SlideShow, PlayBackDirection
        import touchio
        import board

        forward_button = touchio.TouchIn(board.TOUCH4)
        back_button = touchio.TouchIn(board.TOUCH1)

        brightness_up = touchio.TouchIn(board.TOUCH3)
        brightness_down = touchio.TouchIn(board.TOUCH2)

        slideshow = SlideShow()
        slideshow.auto_advance = False
        slideshow.dwell = 0

        while True:
            if forward_button.value:
                slideshow.advance()
            if back_button.value:
                slideshow.advance(direction=PlayBackDirection.BACKWARD)

            if brightness_up.value:
                slideshow.backlight_level_up()
            elif brightness_down.value:
                slideshow.backlight_level_down()
            slideshow.update()
    """

    _max_brightness = 2 ** 15

    # pylint: disable=too-many-arguments
    def __init__(self, folder="/", order=PlayBackMode.RANDOM, loop=True, dwell=3, fade_effect=True,
                 auto_advance=True):
        self._group = displayio.Group()
        board.DISPLAY.show(self._group)
        self._backlight = pulseio.PWMOut(board.TFT_BACKLIGHT)
        self.folder = folder
        """Specifies the folder containing the image files. Default is the root directory, ``"/"``.
        """
        self.loop = loop
        """Specifies whether to loop through the images continuously or play through the list once.
        ``True`` will continue to loop, ``False`` will play only once. Default is `True`."""
        self.dwell = dwell
        """The number of seconds each image displays, in seconds. Default is 3."""
        self.fade_effect = fade_effect
        self._current_state = _LOAD_IMG
        self._img_start = None
        self._file_list = None
        self._images = None
        self._load_images()
        self._order = None
        self.order = order
        self.direction = PlayBackDirection.FORWARD
        """Specify the playback direction.  Default is ``PlayBackDirection.FORWARD``.  Can also be
        ``PlayBackDirection.BACKWARD``."""
        self.auto_advance = auto_advance
        """Enable auto-advance based on dwell time.  Set to ``False`` to manually control."""
        self._update_order()
        self._current_backlight_level = self._max_brightness
    # pylint: enable=too-many-arguments

    @property
    def order(self):
        """Specifies the order in which the images are displayed. Options are random (``RANDOM``) or
        alphabetical (``ALPHA``). Default is ``RANDOM``."""
        return self._order

    @order.setter
    def order(self, order):
        if order not in [PlayBackMode.ALPHA, PlayBackMode.RANDOM]:
            raise ValueError("Order must be either 'RANDOM' or 'ALPHA'")
        if order == self._order:
            return
        self._order = order
        self._update_order()

    def _update_order(self):
        if self.order == PlayBackMode.ALPHA:
            self._file_list = sorted(self._file_list)
        if self.order == PlayBackMode.RANDOM:
            self._file_list = sorted(self._file_list, key=lambda x: random.random())

    def backlight_level_up(self, step=16):
        """Increases the backlight brightness level.

        :param step: Specify the number of steps by which current backlight level will be increased.
                    Default is 16.
        """
        self._max_brightness += step
        if self._max_brightness >= 2 ** 16:
            self._max_brightness = 2 ** 16 - 1
        self._current_backlight_level = self._max_brightness
        return self._current_backlight_level

    def backlight_level_down(self, step=16):
        """Decreases the backlight brightness level.

        :param step: Specify the number of steps by which current backlight level will be decreased.
                    Default is 16.
        """
        self._max_brightness -= step
        if self._max_brightness < 0:
            self._max_brightness = 0
        self._current_backlight_level = self._max_brightness
        return self._current_backlight_level

    def _fade_up(self):
        steps = 100
        for b in range(steps):
            self._backlight.duty_cycle = b * self._current_backlight_level // steps
            time.sleep(0.01)

    def _fade_down(self):
        steps = 100
        for b in range(steps, -1, -1):
            self._backlight.duty_cycle = b * self._current_backlight_level // steps
            time.sleep(0.01)

    def update(self):
        """Updates the slideshow to the next image."""
        now = time.monotonic()
        if self._current_state == _FADE_IN:
            if self.fade_effect:
                self._fade_up()
            else:
                self._backlight.duty_cycle = self._current_backlight_level
            self._current_state = _SHOW_IMG
            self._img_start = time.monotonic()

        if self._current_state == _SHOW_IMG:
            self._backlight.duty_cycle = self._current_backlight_level
            if now - self._img_start > self.dwell:
                self._current_state = _FADE_OUT if self.auto_advance else _WAIT

        if self._current_state == _WAIT:
            self._backlight.duty_cycle = self._current_backlight_level

        if self._current_state == _FADE_OUT:
            if self.fade_effect:
                self._fade_down()
            else:
                self._backlight.duty_cycle = self._current_backlight_level
            self._group.pop()
            self._current_state = _LOAD_IMG

        if self._current_state == _LOAD_IMG:
            try:
                imagename = next(self._images)
            except StopIteration:
                return False
            try:
                self._show_bmp(imagename)
                self._current_state = _FADE_IN
            except ValueError as error:
                print("Incompatible image:", imagename, str(error))

        return True

    def advance(self, direction=None):
        """Displays the next image when `auto_advance` is False.

        Does not advance the image until the current image change is over.

        :param int direction: Change the playback direction when advancing to the next image.
        """
        if direction:
            self.direction = direction
        if self._current_state == _WAIT:
            self._current_state = _FADE_OUT

    def _show_bmp(self, imagename):
        """Opens and loads the image onto the display."""
        with open(imagename, "rb") as image:
            odb = displayio.OnDiskBitmap(image)
            face = displayio.Sprite(odb, pixel_shader=displayio.ColorConverter(), position=(0, 0))
            self._group.append(face)
            board.DISPLAY.wait_for_frame()

    def _get_next_image(self):
        """Cycles through the list of images."""
        index = -1 if self.direction == PlayBackDirection.FORWARD else len(self._file_list)
        while True:
            wrapped = False
            index += self.direction
            if index < 0:
                index = len(self._file_list) - 1
                wrapped = True
            elif index >= len(self._file_list):
                index = 0
                wrapped = True
            yield self._file_list[index]
            if wrapped and not self.loop:
                return

    def _load_images(self):
        """Loads the list of images to be displayed."""
        self._file_list = self._get_filenames()
        self._images = self._get_next_image()

    def _get_filenames(self, extension="bmp"):
        """Creates a list of available image files ending with .bmp in the specified folder."""
        return list(filter(lambda x: x.endswith(extension), os.listdir(self.folder)))
