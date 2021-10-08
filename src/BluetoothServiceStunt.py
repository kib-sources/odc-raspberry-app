import json
import socket
from typing import Optional


class BluetoothServiceStunt:
    _server_sock: socket.socket
    _client_sock: Optional[socket.socket]

    def __init__(self):
        # Arbitrary uuid - must match Android side
        self.sid = "133f71c6-b7b6-437e-8fd1-d2f59cc76066"

        print("creating socket...")
        self._server_sock = socket.socket()
        self._server_sock.bind(("", 14900))
        self._server_sock.listen(1)
        self._client_sock = None

        print("bluetooth service started")

    def listen_for_connections(self):
        while True:
            client_sock, address = self._server_sock.accept()
            print("Connection from ", address)
            self._client_sock = client_sock
            yield client_sock

    def send_to_client(self, msg: str = None, data: dict = None):
        if msg:
            self._client_sock.send(msg.encode("utf-8"))
            return

        if data:
            js = json.dumps(data)
            self._client_sock.send(js.encode("utf-8"))
            return

    def receive_from_client(self) -> str:
        buffer = self._client_sock.recv(100)
        return buffer.decode("utf-8")

    def end_client_session(self):
        self._client_sock.close()
        self._client_sock = None

    def stop(self):
        self._server_sock.close()
