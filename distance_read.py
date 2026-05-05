# /home/zleffler/distance_read.py
import RPi.GPIO as GPIO
import time

TRIG = 5
ECHO = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.output(TRIG, False)
time.sleep(0.05)

readings = []

for _ in range(10):
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10µs pulse
    GPIO.output(TRIG, False)

    # Wait for ECHO to go high — capture start
    timeout = time.perf_counter() + 0.1
    while GPIO.input(ECHO) == 0:
        if time.perf_counter() > timeout:
            break
    pulse_start = time.perf_counter()

    # Wait for ECHO to go low — capture end
    timeout = time.perf_counter() + 0.1
    while GPIO.input(ECHO) == 1:
        if time.perf_counter() > timeout:
            break
    pulse_end = time.perf_counter()

    duration = pulse_end - pulse_start
    distance = (duration * 1000000) / 58  # µs → cm

    if 2 <= distance <= 400:
        readings.append(round(distance, 1))

    time.sleep(0.06)

if readings:
    readings.sort()
    print(round(readings[len(readings) // 2], 1))
else:
    print("ERROR")

GPIO.cleanup()
