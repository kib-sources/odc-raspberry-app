import json
# import bluetooth
import socket
from typing import Optional

# ISocket = Union[bluetooth.BluetoothSocket, socket.socket]
ISocket = socket.socket


class PiService:
    _server_sock: ISocket
    client_sock: Optional[ISocket]

    def __init__(self, server_socket: ISocket):
        self._server_sock = server_socket
        self.client_sock = None

    def listen_for_connections(self):
        while True:
            connection, client_address = self._server_sock.accept()
            # print("Connection from ", client_address)
            print("New Connection")
            self.client_sock = connection
            yield connection

    def send_to_client(self, data: dict):
        js = json.dumps(data)
        buff = (js + "\n").encode("utf-8")
        self.client_sock.sendall(buff)
        return

    def receive_from_client(self) -> str:
        line = ""
        while True:
            buff = self.client_sock.recv(100).decode()
            line += buff
            if "\n" in buff:
                break

        return line

    def end_client_session(self):
        self.client_sock.close()
        self.client_sock = None

    def stop(self):
        if self.client_sock:
            self.client_sock.close()

        self._server_sock.close()

    def is_client_connected(self):
        # banknotes transfer in progress
        if self.client_sock.getblocking():
            return True

        try:
            msg = self.client_sock.recv(1024)
            if msg == b'' or msg == b'end\n':
                return False
        except socket.error:
            pass

        return True


class AtmServiceFactory:
    @staticmethod
    def create_bluetooth_socket() -> PiService:
        # Arbitrary uuid - must match Android side
        sid = "133f71c6-b7b6-437e-8fd1-d2f59cc76066"

        print("creating bluetooth socket...")
        _server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        _server_sock.bind(("", bluetooth.PORT_ANY))
        _server_sock.listen(1)

        bluetooth.advertise_service(
            _server_sock,
            'RPiServer',
            service_id=sid,
            service_classes=[sid, bluetooth.SERIAL_PORT_CLASS],
            profiles=[bluetooth.SERIAL_PORT_PROFILE]
        )
        print("bluetooth service started")

        return PiService(_server_sock)

    @staticmethod
    def create_tcp_socket() -> PiService:
        _server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _server_sock.bind(("", 14900))
        _server_sock.listen(1)
        # print("tcp service started")
        print("bluetooth service started")
        return PiService(_server_sock)
