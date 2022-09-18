import logging as log
import constant
from socket import *

HOST = "127.0.0.1"
PORT = 6543

log.basicConfig(level=log.DEBUG)
log.info(f"Server Address: {HOST}:{PORT}")

def first_packet():
    sequence_number = (constant.FIRST_SEQ_NUMBER).to_bytes(4, byteorder='big')
    operation_type = (constant.UPLOAD).to_bytes(1, byteorder='big')
    filename = "file.txt".encode()
    return sequence_number, operation_type, filename


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    log.debug(f"Sending first message to{(HOST, PORT)}")
    socket.sendto(first_packet(socket), (HOST, PORT))
    log.debug(f"Message sent to{(HOST, PORT)}")
    s.close()
