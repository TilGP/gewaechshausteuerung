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
lcd_columns = 16
lcd_rows    = 2

# Initialisierung I2C Bus
i2c_lcd = busio.I2C(board.SCL, board.SDA)

# Festlegen des LCDs in die Variable LCD
lcd = character_lcd.Character_LCD_I2C(i2c_lcd, lcd_columns, lcd_rows, 0x21)

# Funktion zur Anzeige auf der Matrix je nach Lichtpegel
def display_on_matrix(device, message):
    with canvas(device) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(CP437_FONT))

# Definiere relay pin
relay_pin = 21  # Beispiel-Pin im BCM-Modus, du kannst die Pin-Nummer nach Bedarf anpassen

# BCM Modus GPIO.BCM
GPIO.setmode(GPIO.BCM)
# relay_pin als Ausgang
GPIO.setup(relay_pin, GPIO.OUT)

print("STRG+C Druecken zum Beenden.")

# Matrix Gerät festlegen und erstellen.
serial = spi(port=0, device=1, gpio=noop())
matrix_device = max7219(serial, cascaded=1, block_orientation=90, rotate=0)
# Matrix Initialisierung in der Konsole anzeigen
print("[-] Matrix initialized")

# Lichtsensor initialisieren
class LightSensor():

    def __init__(self):
        self.DEVICE = 0x5c
        self.ONE_TIME_HIGH_RES_MODE_1 = 0x20
        self.bus = smbus.SMBus(1)  # I2C-Bus-Instanz initialisieren, möglicherweise musst du den Bus anpassen

    def convertToNumber(self, data):
        return ((data[1] + (256 * data[0])) / 1.2)

    def readLight(self):
        data = self.bus.read_i2c_block_data(self.DEVICE, self.ONE_TIME_HIGH_RES_MODE_1)
        return self.convertToNumber(data)

light_sensor = LightSensor()
tolerance=100

try:
    while True:
        # Daten vom DHT11-Sensor auslesen
        result = instance.read()

        if result.is_valid():
            temperature = result.temperature / 10.0  # Temperatur mit einer Dezimalstelle
            humidity = result.humidity / 10  # Feuchtigkeit mit einer Dezimalstelle

            # Die Temperatur auf den LCD anzeigen lassen
            round(temperature, 0)
            lcd.message = "Temp: {}C\nHumidity: {}%".format(temperature * 10, int(humidity * 10))

            # Die Temperatur auf dem 7-Segment-LED-Display anzeigen
            segment[0] = str(int(temperature))  # Zehner
            segment[1] = str(int((temperature * 10) % 10)) # Einer
            segment[1] = "." # Punkt als Nachkommastelle
            segment[2] = str(int((temperature * 100) % 10))  # Nachkommastelle
            segment[3] = "C"  # Einheit (Celsius)
            segment.show()

            time.sleep(2) #warten

            # Anzeige der Feuchtigkeit auf dem 7-Segment-LED-Display
            segment[0] = str(int(humidity))  # Zehner
            segment[1] = str(int((humidity * 10) % 10)) # Einer
            segment[1] = "." # Punkt als Nachkommastelle
            segment[2] = str(int((humidity * 100) % 10))  # Nachkommastelle
            segment[3] = "F"  # F für Feuchtigkeit
            segment.show()

            # Aktuellen Lichtpegel messen
            light_level = light_sensor.readLight()


                # Anzeige auf der Matrix je nach Lichtpegel
            if light_level > 700 + tolerance:
                    display_on_matrix(matrix_device, ":o")
                    # schliesse Relais
                    GPIO.output(relay_pin, GPIO.HIGH)
            elif light_level < 700 - tolerance:
                    display_on_matrix(matrix_device, ":(")
                    # Oeffne Relais
                    GPIO.output(relay_pin, GPIO.LOW)
            else:
                    display_on_matrix(matrix_device, ":)")


            # Anzeige der Feuchtigkeit auf dem 7-Segment-LED-Display
            segment[0] = str(int(humidity))  # Zehner
            segment[1] = str(int((humidity * 10) % 10)) # Einer
            segment[1] = "." # Punkt als Nachkommastelle
            segment[2] = str(int((humidity * 100) % 10))  # Nachkommastelle
            segment[3] = "F"  # F für Feuchtigkeit
            segment.show()
        else:
            # Wenn ein DHT11-Fehler auftritt, dann Anzeigen von "FAIL"
            segment.print("FA1L")

        time.sleep(2)  # warten

except KeyboardInterrupt:
    segment.fill(0)
    lcd.clear()
    lcd.backlight = False
    display_on_matrix(matrix_device, "")
    pass
