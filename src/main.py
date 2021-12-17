import logging

from PiService import AtmServiceFactory
from Wallet import Wallet
from banknote_transfer import transfer_banknote
from sm_driver import update_loop


def handle_client_connection():
    print("client connected")

    def on_bucks_inserted(pulse_count):
        print(f"bucks inserted: {pulse_count}")
        transfer_banknote(service, wallet, wallet.banknotes[0])
        del wallet.banknotes[0]

    update_loop(callback=on_bucks_inserted, verbose=True)


if __name__ == "__main__":
    wallet = Wallet()
    wallet.refill(20)

    service = AtmServiceFactory.create_tcp_socket()

    try:
        for client_sock in service.listen_for_connections():
            try:
                handle_client_connection()
            except Exception as e:
                logging.critical("catched error:", exc_info=e)
    except Exception as e:
        service.stop()
        logging.critical("catched error:", exc_info=e)
    except KeyboardInterrupt:
        service.stop()
        print("Interrupted: socket closed")
