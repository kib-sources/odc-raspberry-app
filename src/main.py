import logging
from PiService import AtmServiceFactory
from banknote_transfer import transfer_banknote
from Wallet import Wallet


def main():
    wallet = Wallet()
    wallet.refill(20)

    service = AtmServiceFactory.create_tcp_socket()

    try:
        for client_sock in service.listen_for_connections():
            print("client connected")
            transfer_banknote(service, wallet, wallet.banknotes[0])
            del wallet.banknotes[0]
    except Exception as e:
        service.stop()
        logging.critical("catched error:", exc_info=e)
    except KeyboardInterrupt:
        service.stop()
        print("Interrupted: socket closed")


if __name__ == "__main__":
    main()
