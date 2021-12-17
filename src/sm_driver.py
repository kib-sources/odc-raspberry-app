from time import sleep

import RPi.GPIO as gpio


class SmDriver:
    def __init__(self):
        self.last_pulse_count = 0
        self.pulse_count = 0

        gpio.setmode(gpio.BCM)
        gpio.setup(27, gpio.OUT, initial=gpio.LOW)
        gpio.setup(4, gpio.IN, pull_up_down=gpio.PUD_UP)

        def pulse(channel):
            self.pulse_count += 1

        # GPIO setup
        gpio.add_event_detect(4, gpio.RISING, callback=pulse)

    @staticmethod
    def set_active(is_active):
        gpio.output(27, gpio.HIGH if is_active else gpio.LOW)

    def update_loop(self, callback, *, verbose=False):
        # Update loop
        while True:
            sleep(0.4)
            yield
            if self.pulse_count == 0 or self.last_pulse_count != self.pulse_count:
                self.last_pulse_count = self.pulse_count
                continue

            callback(self.pulse_count)
            if verbose:
                print(f"PULSE {self.pulse_count}")

            self.last_pulse_count = 0
            self.pulse_count = 0
