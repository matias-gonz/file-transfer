import logging as log
import socket
import sys
from os import path

from lib import constant, parser, protocol

HOST = "127.0.0.1"
PORT = 6543


log.basicConfig(level=log.DEBUG)
log.info(f"Server Address: {HOST}:{PORT}")


def send_and_ack(s, msg):
    s.sendto(msg, (HOST, PORT))
    msg, address = s.recvfrom(constant.MAX_PKT_SIZE)
    return msg


def send_request(s, msg):
    attempts = 0
    while True:
        try:
            msg = send_and_ack(s, msg)
            ack = protocol.msg_number(msg)
            log.debug(f"ack {ack}, iseqnum {constant.CONN_START_SEQNUM}")
            if ack == constant.CONN_START_SEQNUM + 1:
                return msg

        except TimeoutError:
            attempts += 1
            if attempts >= constant.RETRY_NUMBER:
                raise


def download():
    p = parser.download_parser()
    args = p.parse_args()
    dst = path.expanduser(args.dst)
    name = args.name

    s = socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(constant.RETRY_DELAY)

    log.debug(f"Sending first message to {(HOST, PORT)}")
    request = protocol.compose_request_msg(constant.DOWNLOAD, name)
    msg = send_request(s, request)
    log.debug(f"First Message sent to {(HOST, PORT)}")

    receiver = protocol.Receiver(dst)

    while True:
        try:
            responses = receiver.respond_to(msg)

            for resp in responses:
                s.sendto(resp, (HOST, PORT))

            try:
                address = tuple()
                while address != (HOST, PORT):
                    msg, address = s.recvfrom(constant.MAX_PKT_SIZE)

            except TimeoutError:
                for resp in receiver.timeout_response():
                    s.sendto(resp, (HOST, PORT))

        except TimeoutError:
            print("Se perdió la conexión con el servidor")
            sys.exit(1)
        except StopIteration:
            break


if __name__ == "__main__":
    download()
