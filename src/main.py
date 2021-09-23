from BluetoothService import BluetoothService


def main():
    service = BluetoothService()

    for client_sock in service.listen_for_connections():
        msg = service.receive_from_client()
        print(msg)
        service.send_to_client("hello from Raspberry Pi4\n")


if __name__ == "__main__":
    main()
