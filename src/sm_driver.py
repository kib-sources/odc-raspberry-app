from time import sleep

import RPi.GPIO as gpio


# Run once to use this API
def initialise_pins():
    gpio.setmode(gpio.BCM)
    gpio.setup(27, gpio.OUT, initial=gpio.LOW)
    gpio.setup(4, gpio.IN, pull_up_down=gpio.PUD_UP)


def set_active(is_active):
    gpio.output(27, gpio.HIGH if is_active else gpio.LOW)


def update_loop(callback, *, verbose=False):
    # Initialising counter
    last_pulse_count = 0
    pulse_count = 0

    def pulse(channel):
        nonlocal pulse_count
        pulse_count += 1

    # GPIO setup
    gpio.add_event_detect(4, gpio.RISING, callback=pulse)

    # Update loop
    while True:
        sleep(0.4)
        yield
        if pulse_count == 0 or last_pulse_count != pulse_count:
            last_pulse_count = pulse_count
            continue

        callback(pulse_count)
        if verbose:
            print(f"PULSE {pulse_count}")

        last_pulse_count = 0
        pulse_count = 0
