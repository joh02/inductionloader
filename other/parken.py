# -*- coding: utf-8 -*-
# IPC per FIFO

# Sender:
import os
fifo_path = "my_fifo"

try:
    os.mkfifo(fifo_path)
except FileExistsError:
    os.remove(fifo_path)

# Öffne die Pipe im Schreibmodus
with open(fifo_path, 'w') as fifo:
    msg = 'msg2'
    fifo.write(msg)

print(f" send: {msg}")

# -------------------------------------------------
# Empfänger
with open(fifo_path, "r") as pipe:

   data = pipe.read()
   print(f'received: {data}')


###############################################################################

# IPC per socket
'''
# Server
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 12345))
server_socket.listen(5)
while True:
    conn, addr = server_socket.accept()
    data = conn.recv(1024)
    print("Received:", data.decode())
    conn.close()

# Client
import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 12345))
client_socket.send(b"Hello, Server!")
client_socket.close()

'''