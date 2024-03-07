from time import sleep
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219
from luma.core.legacy import text

serial = spi(port=0, device=1, gpio=noop())
device = max7219(serial, cascaded=1, block_orientation=90, rotate=0)

# Box and text rendered in portrait mode
device.clear()


# Funktion zur Anzeige auf der Matrix je nach Lichtpegel
def display_on_matrix(device, message):
    with canvas(device) as draw:
        text(draw, (0, 0), message, fill="white")


display_on_matrix(device, ":(")
sleep(10)
display_on_matrix(device, ":)")
sleep(10)
display_on_matrix(device, ":o")
sleep(10)
