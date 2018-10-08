import adafruit_slideshow

# Create the slideshow object
slideshow = adafruit_slideshow.SlideShow()

# Set it to play through only once.
slideshow.loop = False

# Set the order to alphabetical.
slideshow.order = slideshow.ALPHA

while slideshow.update():
    pass
