import time
import board
import RPi.GPIO as GPIO
import dht11
import busio
from adafruit_ht16k33.segments import Seg7x4
import adafruit_character_lcd.character_lcd_i2c as character_lcd
import smbus
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT

LIGHT_LEVEL_TOLERANCE = 5_000
OPTIOMAL_LIGHT_LEVEL = 30_000

# Initialisierung des I2C-Displays
i2c = board.I2C()
segment = Seg7x4(i2c, address=0x70)
segment.fill(0)

# Initialisierung des GPIO-Pins für den DHT11-Sensor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
instance = dht11.DHT11(pin=4)

# Definiere LCD Zeilen und Spaltenanzahl.
LCD_COLUMNS = 16
LCD_ROWS = 2

# Initialisierung I2C Bus
i2c_lcd = busio.I2C(board.SCL, board.SDA)

# Festlegen des LCDs in die Variable LCD
lcd = character_lcd.Character_LCD_I2C(i2c_lcd, LCD_COLUMNS, LCD_ROWS, 0x21)


# Matrix Gerät festlegen und erstellen.
serial = spi(port=0, device=1, gpio=noop())
matrix_device = max7219(serial, cascaded=1, block_orientation=90, rotate=0)
# Matrix Initialisierung in der Konsole anzeigen
print("[-] Matrix initialisiert")


# Funktion zur Anzeige auf der Matrix je nach Lichtpegel
def display_on_matrix(device, message):
    with canvas(device) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(CP437_FONT))


# Lichtsensor initialisieren
class LightSensor:

    def __init__(self):
        self.DEVICE = 0x5C
        self.ONE_TIME_HIGH_RES_MODE_1 = 0x20
        self.bus = smbus.SMBus(
            1
        )  # I2C-Bus-Instanz initialisieren, möglicherweise musst du den Bus anpassen

    def convertToNumber(self, data):
        return (data[1] + (256 * data[0])) / 1.2

    def readLight(self):
        data = self.bus.read_i2c_block_data(self.DEVICE, self.ONE_TIME_HIGH_RES_MODE_1)
        return self.convertToNumber(data)


light_sensor = LightSensor()

try:
    print("STRG+C Druecken zum Beenden.")
    while True:
        # Daten vom DHT11-Sensor auslesen
        result = instance.read()
        while (
            not result.is_valid()
        ):  # Messwerte mit dem DHT11 auslesen, bis das Ergebnis valide ist
            result = instance.read()

        # Die Temperatur auf den LCD anzeigen lassen
        lcd.message = f"Temp: {result.temperature}C\nrH: {result.humidity}%"

        # Anzeige der Temperatur
        segment[0] = str(int(result.temperature / 10))  # Zehnerstelle
        segment[1] = str(int(result.temperature % 10))  # Einerstelle

        # Anzeige der Luftfeuchtigkeit
        segment[2] = str(int(result.humidity / 10))  # Zehnerstelle
        segment[3] = str(int(result.humidity % 10))  # Einerstelle
        segment.colon = True

        segment.show()  # Wird benötigt um die Display LEDs zu updaten.

        # Aktuellen Lichtpegel messen
        light_level = light_sensor.readLight()

        # Anzeige auf der Matrix je nach Lichtpegel
        if light_level > OPTIOMAL_LIGHT_LEVEL + LIGHT_LEVEL_TOLERANCE:  # zu hell
            display_on_matrix(matrix_device, ":o")
        elif light_level < OPTIOMAL_LIGHT_LEVEL - LIGHT_LEVEL_TOLERANCE:  # zu dunkel
            display_on_matrix(matrix_device, ":(")
        else:  # optimal
            display_on_matrix(matrix_device, ":)")

        time.sleep(1)  # warten

except KeyboardInterrupt:
    segment.fill(0)
    lcd.clear()
    lcd.backlight = False
    display_on_matrix(matrix_device, "")
    pass
