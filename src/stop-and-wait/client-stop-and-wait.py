import sys
sys.path.append('.')  # noqa: E402
from src.parser import parser as p
import logging as log
from socket import socket, AF_INET, SOCK_DGRAM, timeout
import src.lib.constant as constant

HOST = "127.0.0.1"
PORT = 6543
SOCKET_TIMEOUT = 0.030  # 30 ms
MAX_ATTEMPTS = 180


log.basicConfig(level=log.DEBUG)
log.info(f"Server Address: {HOST}:{PORT}")


def first_packet(name):
    operation_type = constant.UPLOAD.to_bytes(1, byteorder="big")
    filename = name.encode()
    return operation_type + filename


def increase_seqnum(iseqnum):
    seqnum = iseqnum.to_bytes(4, byteorder="big")
    iseqnum += 1
    return iseqnum, seqnum


def sendto_and_ack(s, data):
    s.sendto(data, (HOST, PORT))
    msg, address = s.recvfrom(4)
    return int.from_bytes(msg[:4], byteorder="big")


def sendto(s, iseqnum, data):
    attempts = 0
    iseqnum, seqnum = increase_seqnum(iseqnum)
    while True:
        try:
            ack = sendto_and_ack(s, seqnum + data)
            if ack == iseqnum:
                return iseqnum

        except timeout:
            attempts += 1
            if attempts >= MAX_ATTEMPTS:
                raise


def upload():
    parser = p.upload_parser()
    args = parser.parse_args()
    src = args.src
    name = args.name

    s = socket(AF_INET, SOCK_DGRAM)
    s.settimeout(SOCKET_TIMEOUT)

    log.debug(f"Sending first message to {(HOST, PORT)}")
    iseqnum = constant.CONN_START_SEQNUM
    iseqnum = sendto(s, iseqnum, first_packet(name))
    log.debug(f"First Message sent to {(HOST, PORT)}")

    sended_data = 0
    file = open(src, "rb")
    data = file.read(constant.PAYLOAD_SIZE)

    data = bytearray(data)
    while data:
        log.debug(
            f"Sending {len(data)} bytes of data, sequence number is {iseqnum}")
        iseqnum = sendto(s, iseqnum, data)
        sended_data += len(data)
        data = file.read(constant.PAYLOAD_SIZE)

    log.debug(f"Sending sequence number is {iseqnum} with no data")
    seqnum = iseqnum.to_bytes(4, byteorder="big")
    s.sendto(seqnum, (HOST, PORT))
    log.debug(f"sended_data {sended_data} bytes of data")
    s.close()
    file.close()


upload()
