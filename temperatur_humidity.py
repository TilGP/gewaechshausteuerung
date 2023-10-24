#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
import board
import RPi.GPIO as GPIO
import dht11

# aus dem Adafruit_LED_Backpack die 7-Segment-Display Klasse importieren.
from adafruit_ht16k33.segments import Seg7x4

i2c = board.I2C()
segment = Seg7x4(i2c, address=0x70) # segment der I2C Adresse 0x70 und die Displaydefinition zuweisen

segment.fill(0) # Initialisierung des Displays. Muss einmal ausgeführt werden bevor das Display benutzt wird.

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# Daten über DHT11 auslesen
instance = dht11.DHT11(pin = 4)

print("STRG+C Druecken zum beenden.") # print Befehl für Ausgabe zum beenden des Scriptes

# Schleife, die durchgängig die Temperatur misst und diese auf dem Segment-Display anzeigt
try:
  while(True):
    
    result = instance.read()
    while not result.is_valid(): # lesen, bis das Ergebnis valide ist 
        result = instance.read()
    print("temp: ", result.temperature)
    print("humidity: ", result.humidity)

    segment.fill(0)

    # Anzeige der Temperatur
    segment[0] =  str(int(result.temperature / 10))          # Zehnerzahlen
    segment[1] =   str(int(result.temperature % 10))         # Einerzahlen
    
    # Anzeige der Luftfeuchtigkeit
    segment[2] = str(int(result.humidity / 10))
    segment[3] = str(int(result.humidity % 10))
    segment.colon = False


    segment.show() # Wird benötigt um die Display LEDs zu updaten.

    time.sleep(20) # Warte zwei Sekunden
except KeyboardInterrupt: # Fange ein STRG+C ab und schalte das Display aus
    segment.fill(0)
