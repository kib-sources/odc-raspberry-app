import logging
import socket

from sm_driver import SmDriver
from PiService import AtmServiceFactory
from Wallet import Wallet
from banknote_transfer import transfer_banknotes


def handle_client_connection():
    logging.debug("client connected")

    def on_bucks_inserted(pulse_count):
        service.client_sock.setblocking(True)
        transfer_banknotes(service, wallet, pulse_count)
        service.client_sock.setblocking(False)

    sm_driver.set_active(is_active=True)
    service.client_sock.setblocking(False)

    for _ in sm_driver.update_loop(callback=on_bucks_inserted, verbose=True):
        # banknotes transfer in progress
        if service.client_sock.getblocking():
            continue

        try:
            msg = service.client_sock.recv(1024)
            if msg == b'' or msg == b'make me cum\n':
                raise Exception("client disconnected")
        except socket.error:
            pass


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
                logging.error("client disconnected", exc_info=e)
                sm_driver.set_active(is_active=False)
                client_sock.close()
                service.client_sock = None
    except Exception as e:
        service.stop()
        logging.critical("catched error:", exc_info=e)
    except KeyboardInterrupt:
        service.stop()
        logging.warning("Interrupted: socket closed")
