Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-slideshow/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/slideshow/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://discord.gg/nBQh6qu
    :alt: Discord

.. image:: https://travis-ci.com/adafruit/Adafruit_CircuitPython_Slideshow.svg?branch=master
    :target: https://travis-ci.com/adafruit/Adafruit_CircuitPython_Slideshow
    :alt: Build Status

CircuitPython helper library for displaying a slideshow of images on a display.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Usage Example
=============

.. code-block:: python

    from adafruit_slideshow import PlayBackOrder, SlideShow
    import board
    import pulseio

    # Create the slideshow object that plays through once alphabetically.
    slideshow = SlideShow(board.DISPLAY, pulseio.PWMOut(board.TFT_BACKLIGHT), folder="/",
                          loop=False, order=PlayBackOrder.ALPHABETICAL)

    while slideshow.update():
        pass

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/adafruit_CircuitPython_Slideshow/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
