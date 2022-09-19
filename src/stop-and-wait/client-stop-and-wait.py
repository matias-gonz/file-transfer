import logging as log
from socket import *

import constant

HOST = "127.0.0.1"
PORT = 6543

log.basicConfig(level=log.DEBUG)
log.info(f"Server Address: {HOST}:{PORT}")

def first_packet():
    sequence_number = (constant.FIRST_SEQ_NUMBER).to_bytes(4, byteorder="big")
    operation_type = (constant.UPLOAD).to_bytes(1, byteorder="big")
    filename = "prueba.txt".encode()
    return sequence_number + operation_type + filename

def upload():
    client_socket = socket(AF_INET, SOCK_DGRAM)
    log.debug(f"Sending first message to{(HOST, PORT)}")
    client_socket.sendto(first_packet(), (HOST, PORT))
    log.debug(f"First Message sent to{(HOST, PORT)}")
    file = open(constant.FILEPATH + "prueba.txt", "rb")
    data = file.read(constant.PAYLOAD_SIZE)
    next_sequence_number = 1
    data = bytearray(data)
    while data:
        sequence_number = (next_sequence_number).to_bytes(4, byteorder="big")
        if client_socket.sendto(sequence_number+data, (HOST, PORT)):
            log.debug("Sending data packets")
            data = file.read(constant.PAYLOAD_SIZE)
        next_sequence_number += 1
    client_socket.sendto((next_sequence_number).to_bytes(4, byteorder="big"), (HOST, PORT))
    client_socket.close()
    file.close()


upload()
