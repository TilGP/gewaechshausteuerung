from time import sleep
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219

serial = spi(port=0, device=1, gpio=noop())
device = max7219(serial, rotate=1)

# Box and text rendered in portrait mode
device.clear()

with canvas(device) as draw:
    print(dir(draw.shape.__init__))
    # draw.rectangle(device.bounding_box, outline="white", fill="black")

# sleep(10)
