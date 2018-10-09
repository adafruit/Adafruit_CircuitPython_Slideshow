from adafruit_slideshow import PlayBackMode, SlideShow

# Create the slideshow object
slideshow = SlideShow()

# Set it to play through only once.
slideshow.loop = False

# Set the order to alphabetical.
slideshow.order = PlayBackMode.ALPHA

while slideshow.update():
    pass
