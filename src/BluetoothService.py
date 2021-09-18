import bluetooth


class BluetoothService:
    def __init__(self):
        # Arbitrary uuid - must match Android side
        self.sid = "133f71c6-b7b6-437e-8fd1-d2f59cc76066"

        print("creating socket...")
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock.bind(("", bluetooth.PORT_ANY))
        self.server_sock.listen(1)

        bluetooth.advertise_service(
            self.server_sock,
            'RPiServer',
            service_id=self.sid,
            service_classes=[self.sid, bluetooth.SERIAL_PORT_CLASS],
            profiles=[bluetooth.SERIAL_PORT_PROFILE]
        )
        print("bluetooth service started")

    def listen_for_connections(self):
        while True:
            client_sock, address = self.server_sock.accept()
            print("Connection from ", address)
            yield client_sock

    def stop(self):
        self.server_sock.close()
