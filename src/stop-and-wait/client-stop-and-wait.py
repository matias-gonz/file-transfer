import sys
sys.path.append('.')  # noqa: E402
from src.parser import parser as p
import logging as log
from socket import socket, AF_INET, SOCK_DGRAM, timeout
import src.lib.constant as constant
import src.lib.protocol as protocol

HOST = "127.0.0.1"
PORT = 6543
SOCKET_TIMEOUT = 0.030  # 30 ms
MAX_ATTEMPTS = 180


log.basicConfig(level=log.DEBUG)
log.info(f"Server Address: {HOST}:{PORT}")


def sendto_and_ack(s, msg):
    s.sendto(msg, (HOST, PORT))
    msg, address = s.recvfrom(4)
    return protocol.msg_number(msg)


def sendto(s, iseqnum, msg):
    attempts = 0
    iseqnum += 1
    while True:
        try:
            ack = sendto_and_ack(s, msg)
            log.debug(f"ack {ack}, iseqnum {iseqnum}")
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
    msg = protocol.compose_request_msg(constant.UPLOAD, name)
    iseqnum = sendto(s, iseqnum, msg)
    log.debug(f"First Message sent to {(HOST, PORT)}")

    sended_data = 0
    file = open(src, "rb")
    data = file.read(constant.PAYLOAD_SIZE)

    data = bytearray(data)
    while data:
        log.debug(
            f"Sending {len(data)} bytes of data, sequence number is {iseqnum}")
        msg = protocol.compose_msg(iseqnum, data)
        iseqnum = sendto(s, iseqnum, msg)
        sended_data += len(data)
        data = file.read(constant.PAYLOAD_SIZE)

    log.debug(f"Sending sequence number is {iseqnum} with no data")
    msg = protocol.compose_msg(iseqnum)
    s.sendto(msg, (HOST, PORT))
    log.debug(f"sended_data {sended_data} bytes of data")
    s.close()
    file.close()


upload()
