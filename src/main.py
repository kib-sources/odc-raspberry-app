import logging

from PiService import AtmServiceFactory
from Wallet import Wallet
from banknote_transfer import transfer_banknotes
import sm_driver


def handle_client_connection():
    print("client connected")

    def on_bucks_inserted(pulse_count):
        print("on_bucks_inserted")
        transfer_banknotes(service, wallet, pulse_count)

    sm_driver.set_active(is_active=True)
    print("sm_driver is_active, running loop...")
    sm_driver.update_loop(callback=on_bucks_inserted, verbose=True)
    print("loop ended!")


if __name__ == "__main__":
    wallet = Wallet()
    logging.info("refilling banknotes bag...")
    wallet.refill(10000)

    service = AtmServiceFactory.create_tcp_socket()
    sm_driver.initialise_pins()

    try:
        for client_sock in service.listen_for_connections():
            try:
                handle_client_connection()
            except Exception as e:
                print("client disconnected")
                sm_driver.set_active(is_active=False)
    except Exception as e:
        service.stop()
        logging.critical("catched error:", exc_info=e)
    except KeyboardInterrupt:
        service.stop()
        logging.warning("Interrupted: socket closed")
