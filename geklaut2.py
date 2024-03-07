#!/usr/bin/python

import RPi.GPIO as GPIO
import time

# Definiere relay pin
relay_pin = 21  # Beispiel-Pin im BCM-Modus, du kannst die Pin-Nummer nach Bedarf anpassen

# BCM Modus GPIO.BCM
GPIO.setmode(GPIO.BCM)
# relay_pin als Ausgang
GPIO.setup(relay_pin, GPIO.OUT)

# Oeffne Relais
GPIO.output(relay_pin, GPIO.LOW)
# warte eine halbe Sekunde
time.sleep(0.5)
# schliesse Relais
GPIO.output(relay_pin, GPIO.HIGH)

# GPIO zurücksetzen
GPIO.cleanup()
