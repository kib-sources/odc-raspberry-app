from BluetoothServiceStunt import BluetoothServiceStunt
from banknote_transfer import transfer_banknote
from core.Wallet import Wallet
import logging


def main():
    wallet = Wallet()
    wallet.refill(300)

    service = BluetoothServiceStunt()

    try:
        for client_sock in service.listen_for_connections():
            msg = service.receive_from_client()
            print(msg)
            transfer_banknote(service, wallet, wallet.banknotes[0])
    except BaseException as e:
        service.stop()
        logging.critical("", exc_info=e)


if __name__ == "__main__":
    main()
