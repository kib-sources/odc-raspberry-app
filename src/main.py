import logging
import time

from PiService import AtmServiceFactory
from NfcService import NfcServiceFactory, NfcService
from Wallet import Wallet
from banknote_transfer import transfer_banknotes
from sm_driver import SmDriver

logging.getLogger().setLevel(logging.INFO)

inserted_sum = 0


def handle_client_connection():
    logging.debug("client connected")

    def on_bucks_inserted(pulse_count):
        service.client_sock.setblocking(True)
        transfer_banknotes(service, wallet, pulse_count)
        service.client_sock.setblocking(False)

    sm_driver.set_active(is_active=True)
    service.client_sock.setblocking(False)

    for _ in sm_driver.update_loop(callback=on_bucks_inserted):
        if not service._is_client_connected():
            break


def curr_ms():
    return round(time.time() * 1000)


def start_atm():
    def on_bucks_inserted(pulse_count):
        banknote_map = {2: 50, 3: 100, 4: 500, 5: 1000, 6: 5000, 7: 200, 8: 2000}
        global inserted_sum
        print("Pulse count is: " + str(pulse_count))
        inserted_sum += banknote_map[pulse_count]
        print("Sum is: " + str(inserted_sum))

    def on_nfc_device_found(transfer_service: NfcService):
        global inserted_sum
        if inserted_sum:
            transfer_banknotes(transfer_service, wallet, inserted_sum)
            inserted_sum = 0

    sm_driver.set_active(is_active=True)
    nfc_service = NfcServiceFactory.create_nfc_socket()

    sm_iterator = sm_driver.update_loop(callback=on_bucks_inserted)
    nfc_iterator = nfc_service.listen_for_connection(callback=on_nfc_device_found)

    while True:
        t = curr_ms()
        next(sm_iterator)

        while curr_ms() - t < 400:
            next(nfc_iterator)


if __name__ == "__main__":
    wallet = Wallet()
    wallet.refill(20000)

    bluetooth = False
    nfc = True

    sm_driver = SmDriver()
    if nfc:
        start_atm()

    elif bluetooth:
        service = AtmServiceFactory.create_tcp_socket()
        try:
            for client_sock in service.listen_for_connections():
                try:
                    handle_client_connection()
                except Exception as e:
                    logging.error("err", exc_info=e)

                logging.info("client disconnected")
                sm_driver.set_active(is_active=False)
                client_sock.close()
                service.client_sock = None
        except Exception as e:
            service.stop()
            logging.critical("catched error:", exc_info=e)
        except KeyboardInterrupt:
            service.stop()
            logging.warning("Interrupted: socket closed")
