import RPi.GPIO as GPIO
import time

# definiere Relay Pin
relay_pin = 21

GPIO.setmode(GPIO.BOARD)
GPIO.setup(relay_pin, GPIO.OUT)

GPIO.output(relay_pin, GPIO.LOW)  # an
time.sleep(0.5)
GPIO.output(relay_pin, GPIO.HIGH)  # aus
GPIO.cleanup()
