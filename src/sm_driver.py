import logging
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
        """Устанавливает купюроприемник в состояние вкл/выкл
        :param is_active: флаг, отвечающий за состояние, в которое будет переведен купюроприемник
        """
        gpio.output(27, gpio.HIGH if is_active else gpio.LOW)

    def update_loop(self, callback):
        """Ожидает сигнал от купюроприемника о приеме курюры
        :param callback: функция, которая будет вызвана при вставке купюры
        """

        while True:
            yield
            if self.pulse_count == 0 or self.last_pulse_count != self.pulse_count:
                self.last_pulse_count = self.pulse_count
                continue

            callback(self.pulse_count)
            logging.debug(f"PULSE {self.pulse_count}")

            self.last_pulse_count = 0
            self.pulse_count = 0
