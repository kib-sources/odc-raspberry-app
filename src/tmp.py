import socket

from PiService import AtmServiceFactory

if __name__ == "__main__":
    service = AtmServiceFactory.create_tcp_socket()

    try:
        for client_sock in service.listen_for_connections():
            client_sock.setblocking(False)

            while True:
                try:
                    msg = service.client_sock.recv(1024)
                    if msg == b'' or msg == b'make me cum\n':
                        break

                    print(msg)
                except socket.error:
                    pass

            # client_sock.close()
            # service.client_sock = None

    except KeyboardInterrupt:
        service.stop()
        print("Interrupted: socket closed")
