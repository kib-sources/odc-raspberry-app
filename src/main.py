from AtmService import AtmService, ServerSocketFactory
from banknote_transfer import transfer_banknote
from core.Wallet import Wallet
import logging


def main():
    wallet = Wallet()
    wallet.refill(300)

    socket = ServerSocketFactory.create_tcp_socket()
    service = AtmService(socket)

    try:
        for client_sock in service.listen_for_connections():
            print("client connected")
            transfer_banknote(service, wallet, wallet.banknotes[0])
    except Exception as e:
        socket.close()
        logging.critical("catched error:", exc_info=e)
    except KeyboardInterrupt:
        socket.close()
        print("Interrupted: socket closed")


if __name__ == "__main__":
    main()
