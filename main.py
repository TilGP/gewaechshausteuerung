import csv
import os
import time
from datetime import datetime

import adafruit_character_lcd.character_lcd_i2c as character_lcd
import board
import busio
import dht11
import RPi.GPIO as GPIO
import smbus
from adafruit_ht16k33.segments import Seg7x4
from luma.core.interface.serial import noop, spi
from luma.core.legacy import text
from luma.core.legacy.font import CP437_FONT, proportional
from luma.core.render import canvas
from luma.led_matrix.device import max7219

LIGHT_LEVEL_TOLERANCE = 5_000
OPTIOMAL_LIGHT_LEVEL = 40_000

csv_file_name = "data.csv"
file_exists = False
if os.path.exists(csv_file_name):
    file_exists = True

csv_file = open(csv_file_name, "a", newline="")  # Datei im "append" Modus öffnen
csv_writer = csv.writer(csv_file)

if (
    not file_exists
):  # Wenn die Datei noch nicht existiert, dann soll der Header geschrieben werden
    csv_writer.writerow(
        [
            "Datum",
            "Zeit",
            "Temperatur (in °C)",
            "Luftfeuchtigkeit (in %)",
            "Helligkeit (in Lux)",
            "Relay Status",
        ]
    )

# Initialisierung des I2C-Displays
i2c = board.I2C()
segment = Seg7x4(i2c, address=0x70)
segment.fill(0)

# Initialisierung des GPIO-Pins für den DHT11-Sensor
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
instance = dht11.DHT11(pin=4)

# Setze den Relay Pin auf aus
RELAY_PIN = 40
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)
reelay_state = False

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
            if reelay_state:
                GPIO.output(RELAY_PIN, GPIO.LOW)
                reelay_state = False
        elif light_level < OPTIOMAL_LIGHT_LEVEL - LIGHT_LEVEL_TOLERANCE:  # zu dunkel
            display_on_matrix(matrix_device, ":(")
            if not reelay_state:
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                reelay_state = True
        else:  # optimal
            display_on_matrix(matrix_device, ":)")

        dt = datetime.now()
        csv_writer.writerow(  # Schreibe die Messwerte in die CSV-Datei
            [
                dt.strftime("%d.%m.%Y"),
                dt.strftime("%H:%M:%S"),
                round(result.temperature, 2),
                round(result.humidity, 2),
                round(light_level, 2),
                "An" if reelay_state else "Aus",
            ]
        )

        time.sleep(1)  # warten

except KeyboardInterrupt:  # Wenn STRG+C gedrückt wird, dann...
    csv_file.close()  # ... schließe die CSV-Datei
    segment.fill(0)  # Lösche die Anzeige auf dem 7-Segment-Display
    lcd.clear()  # Lösche die Anzeige auf dem LCD
    lcd.backlight = False  # Schalte die Hintergrundbeleuchtung des LCDs aus
    display_on_matrix(matrix_device, "")  # Lösche die Anzeige auf der Matrix
