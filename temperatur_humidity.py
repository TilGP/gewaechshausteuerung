#!/usr/bin/python
# V4

import time
import datetime
import board
import RPi.GPIO as GPIO
import busio
import dht11

# aus dem Adafruit_LED_Backpack die 7-Segment-Display Klasse importieren.
from adafruit_ht16k33.segments import Seg7x4
import adafruit_character_lcd.character_lcd_i2c as character_lcd

i2c = busio.I2C(board.SCL, board.SDA)
segment = Seg7x4(i2c, address=0x70) # segment der I2C Adresse 0x70 und die Displaydefinition zuweisen

segment.fill(0) # Initialisierung des Displays. Muss einmal ausgeführt werden bevor das Display benutzt wird.

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# Definiere LCD Zeilen und Spaltenanzahl.
lcd_columns = 16
lcd_rows    = 2

#Festlegen des LCDs in die Variable LCD
lcd = character_lcd.Character_LCD_I2C(i2c, lcd_columns, lcd_rows, 0x21)

# Hintergrundbeleuchtung einschalten
lcd.backlight = True  

# DHT11-Sensor Instanz initialisieren 
instance = dht11.DHT11(pin = 4)

print("STRG+C Druecken zum beenden.") # print Befehl für Ausgabe zum beenden des Scriptes

# Schleife, die durchgängig die Temperatur misst und diese auf dem Segment-Display anzeigt
try:
  while(True):
    
    result = instance.read()
    while not result.is_valid(): # Messwerte mit dem DHT11 auslesen, bis das Ergebnis valide ist 
        result = instance.read()
    print("temp: ", result.temperature)
    print("humidity: ", result.humidity)

    segment.fill(0)

    # Anzeige der Temperatur
    segment[0] =  str(int(result.temperature / 10)) # Zehnerstelle
    segment[1] =  str(int(result.temperature % 10)) # Einerstelle
    
    # Anzeige der Luftfeuchtigkeit
    segment[2] = str(int(result.humidity / 10)) # Zehnerstelle
    segment[3] = str(int(result.humidity % 10)) # Einerstelle
    segment.colon = False


    segment.show() # Wird benötigt um die Display LEDs zu updaten.
    lcd.message = f"temp: {result.temperature}\nhumidity: {result.humidity}"

    time.sleep(20) # Warte zwei Sekunden
except KeyboardInterrupt: # Fange ein STRG+C ab und schalte das Display aus
    segment.fill(0)
    
    # LCD ausschalten.
    lcd.clear()
    lcd.backlight = False
