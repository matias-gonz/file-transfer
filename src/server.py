import logging as log
import socket

HOST = "127.0.0.1"
PORT = 6543

log.basicConfig(level=log.DEBUG)
log.info(f"Address: {HOST}:{PORT}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    log.debug(f"Socket binded to {(HOST, PORT)}")
    s.listen()
    conn, addr = s.accept()
    with conn:
        log.info(f"Connected by {addr}")
        data = conn.recv(1024)
        print(data.decode())
