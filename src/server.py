import logging as log
import socket
from parser import parser

args = parser.parse_args()
host = args.host
port = args.port

log.basicConfig(level=log.DEBUG)
log.info(f"Address: {host}:{port}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    log.debug(f"Socket binded to {(host, port)}")
    s.listen()
    conn, addr = s.accept()
    with conn:
        log.info(f"Connected by {addr}")
        data = conn.recv(1024)
        print(data.decode())
