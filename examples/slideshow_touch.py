from adafruit_slideshow import PlayBackMode, SlideShow, PlayBackDirection
import touchio
import board

forward_button = touchio.TouchIn(board.TOUCH4)
back_button = touchio.TouchIn(board.TOUCH1)

brightness_up = touchio.TouchIn(board.TOUCH3)
brightness_down = touchio.TouchIn(board.TOUCH2)

slideshow = SlideShow()
slideshow.order = PlayBackMode.ALPHA
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
