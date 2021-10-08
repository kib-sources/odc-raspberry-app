from BluetoothServiceStunt import BluetoothServiceStunt


def main():
    service = BluetoothServiceStunt()

    for client_sock in service.listen_for_connections():
        msg = service.receive_from_client()
        print(msg)
        service.send_to_client("hello from Raspberry Pi4\n")
        print("goodbye")


if __name__ == "__main__":
    main()
