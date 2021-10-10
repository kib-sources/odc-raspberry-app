import json
from typing import Optional, Union
import bluetooth
import socket


ISocket = Union[bluetooth.BluetoothSocket, socket.socket]


class AtmService:
    _server_sock: ISocket
    _client_sock: Optional[ISocket]

    def __init__(self, server_socket: ISocket):
        self._server_sock = server_socket
        self._client_sock = None

    def listen_for_connections(self):
        while True:
            connection, client_address = self._server_sock.accept()
            print("Connection from ", client_address)
            self._client_sock = connection
            yield connection

    def send_to_client(self, data: dict):
        js = json.dumps(data)
        print("sending: ", js)
        buff = (js + "\n").encode("utf-8")
        self._client_sock.sendall(buff)
        return

    def receive_from_client(self) -> str:
        buffer = self._client_sock.recv(100)
        print("received", buffer)
        return buffer

    def end_client_session(self):
        self._client_sock.close()
        self._client_sock = None

    def stop(self):
        self._server_sock.close()


class ServerSocketFactory:
    @staticmethod
    def create_bluetooth_socket() -> bluetooth.BluetoothSocket:
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

        return _server_sock

    @staticmethod
    def create_tcp_socket() -> socket.socket:
        _server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _server_sock.bind(("", 14900))
        _server_sock.listen(1)
        print("tcp service started")
        return _server_sock
