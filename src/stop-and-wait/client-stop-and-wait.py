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
    return sequence_number + operation_type + filename

def upload():
    client_socket = socket(AF_INET, SOCK_DGRAM)
    log.debug(f"Sending first message to{(HOST, PORT)}")
    client_socket.sendto(first_packet(), (HOST, PORT))
    log.debug(f"First Message sent to{(HOST, PORT)}")
    file = open (constant.FILEPATH+'prueba.txt',"rb")
    data = file.read(constant.MAX_PKT_SIZE)
    while (data):
        if (client_socket.sendto(data, (HOST, PORT))):
            log.debug("Sending data packets")
            data = file.read(constant.MAX_PKT_SIZE)
    client_socket.close()
    file.close()


upload()