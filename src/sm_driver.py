import asyncio
import logging
import threading
import time
from time import sleep

import RPi.GPIO as gpio


class SmDriver:
    def __init__(self):
        self.last_pulse_count = 0
        self.pulse_count = 0

        gpio.setmode(gpio.BCM)
        gpio.setup(27, gpio.OUT, initial=gpio.LOW)
        gpio.setup(9, gpio.IN, pull_up_down=gpio.PUD_UP)

        def pulse(channel):
            self.pulse_count += 1

        def listen_for_pulse():
            last_level = gpio.input(9)
            while True:
                level = gpio.input(9)
                # print('level ', level, ' last ', last_level)
                if level != last_level and level == 0:
                    print(f'PULSE: Last level: {last_level}; Current level: {level}')
                    pulse(level)
                last_level = level
                time.sleep(0.0025)

        threading.Thread(target=listen_for_pulse).start()

    @staticmethod
    def set_active(is_active):
        """Устанавливает купюроприемник в состояние вкл/выкл
        :param is_active: флаг, отвечающий за состояние, в которое будет переведен купюроприемник
        """
        gpio.output(27, gpio.HIGH if is_active else gpio.LOW)

    def update_loop(self, callback):
        """Ожидает сигнал от купюроприёмника о приеме купюры
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
