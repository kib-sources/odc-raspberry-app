from BluetoothService import BluetoothService

service = BluetoothService()

for client_sock in service.listen_for_connections():
    buffer = client_sock.recv(100)
    print(buffer)

    client_sock.send(b"hello from Raspberry Pi4\n")

