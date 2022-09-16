import logging as log
import socket

HOST = "127.0.0.1"
PORT = 6543

log.basicConfig(level=log.DEBUG)
log.info(f"Server Address: {HOST}:{PORT}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    log.debug(f"Initiating connection to {(HOST, PORT)}")
    s.connect((HOST, PORT))
    log.debug(f"Connected to {(HOST, PORT)}")
    s.sendall("I'm the client".encode())
    s.close()
