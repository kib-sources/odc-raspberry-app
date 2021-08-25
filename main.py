import bluetooth

print("creating socket...")
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)
port = server_sock.getsockname()[1]

#Arbitrary uuid - must match Android side
sid = "133f71c6-b7b6-437e-8fd1-d2f59cc76066"

print("bluetooth service starting...")
bluetooth.advertise_service(server_sock,
        'RPiServer',
        service_id = sid,
        service_classes = [sid, bluetooth.SERIAL_PORT_CLASS],
        profiles = [bluetooth.SERIAL_PORT_PROFILE]
    )
print("bluetooth service started")

while True:
	client_sock, address = server_sock.accept()
	print("Connection from ", address)


	buffer = client_sock.recv(100)
	print(buffer)

	client_sock.send(b"hello from Raspberry Pi4\n")
	#client_sock.close()


server_sock.close()
