import socket

HOST = "127.0.0.1"
PORT = 6543

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall("I'm the client".encode())
    s.close()
