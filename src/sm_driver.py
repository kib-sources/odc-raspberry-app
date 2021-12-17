from time import sleep

import RPi.GPIO as gpio


def update_loop(callback, *, verbose=False):
    # Initialising counter
    last_pulse_count = 0
    pulse_count = 0

    def pulse(channel):
        nonlocal pulse_count
        pulse_count += 1

    # GPIO setup
    gpio.setmode(gpio.BCM)
    gpio.setup(4, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(4, gpio.RISING, callback=pulse)

    # Update loop
    while True:
        sleep(0.4)

        if pulse_count == 0 or last_pulse_count != pulse_count:
            last_pulse_count = pulse_count
            continue

        callback(pulse_count)
        if verbose:
            print(f"PULSE {pulse_count}")

        last_pulse_count = 0
        pulse_count = 0


def disable_sm():
    pass
