#!/usr/bin/python
# TCP Server, Chapter 2, "Black Hat Python"
# Simple TCP server
#
import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print("[*] Listening on {}:{}".format(bind_ip, bind_port))


# This is our client-handling thread
def handle_client(client_socket):
    # Print out what the client sends
    request = client_socket.recv(1024)

    print("[*] Received: {}".format(request.decode('utf-8')))

    # Send back a packet
    client_socket.send("ACK!".encode('utf-8'))

    client_socket.close()


while True:
    client, addr = server.accept()

    print("[*] Accepted connection from: {}:{}".format(addr[0], addr[1]))

    # spin up our client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
