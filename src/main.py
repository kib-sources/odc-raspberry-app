import logging

from PiService import AtmServiceFactory
from Wallet import Wallet
from banknote_transfer import transfer_banknotes
from sm_driver import SmDriver

logging.getLogger().setLevel(logging.INFO)


def handle_client_connection():
    logging.debug("client connected")

    def on_bucks_inserted(pulse_count):
        service.client_sock.setblocking(True)
        transfer_banknotes(service, wallet, pulse_count)
        service.client_sock.setblocking(False)

    sm_driver.set_active(is_active=True)
    service.client_sock.setblocking(False)

    for _ in sm_driver.update_loop(callback=on_bucks_inserted):
        if not service.is_client_connected():
            break


if __name__ == "__main__":
    wallet = Wallet()
    wallet.refill(10000)

    service = AtmServiceFactory.create_tcp_socket()
    sm_driver = SmDriver()

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
