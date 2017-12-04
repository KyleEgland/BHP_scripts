#!/usr/bin/python
# TCP Client, Chapter 2, "Black Hat Python"
# Simple TCP client
import socket

target_host = "127.0.0.1"
target_port = 9999

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the client
client.connect((target_host, target_port))

# send some data
client.send("ABCDEF".encode('utf-8'))

# Receive some data
response = client.recv(4096)

printable = response.decode('utf-8')

print(printable)
