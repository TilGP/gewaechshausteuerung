#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
import board
import RPi.GPIO as GPIO
import dht11

#from Adafruit_LED_Backpack import SevenSegment
from adafruit_ht16k33.segments import Seg7x4

i2c = board.I2C()
segment = Seg7x4(i2c, address=0x70) #segment der I2C Adresse 0x70 und die Displaydefinition zuweisen

segment.fill(0) # Initialisierung des Displays. Muss einmal ausgeführt werden bevor das Display benutzt wird.

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

# read data using pin 14
instance = dht11.DHT11(pin = 4)

print ("STRG+C Druecken zum beenden.") #print Befehl für Ausgabe zum beenden des Scriptes

#Schleife welche dauerhaft die Zeit updated und sie auf dem Display anzeigt.
try:
  while(True):
    
    result = instance.read()
    while not result.is_valid(): # read until valid values
        result = instance.read()
    print(result.temperature)

    segment.fill(0)

    # Anzeige für die Stunden.
    segment[0] =  str(int(result.temperature / 10))          # Zehnerzahlen
    segment[1] =   str(int(result.temperature % 10))         # Einerzahlen
    segment.colon = False


    segment.show() # Wird benötigt um die Display LEDs zu updaten.

    time.sleep(20) # Warte eine Sekunde
except KeyboardInterrupt:
    segment.fill(0)
