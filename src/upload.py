import logging as log
import socket
import sys
from os import path

from lib import constant, parser, protocol


def send_and_ack(s, addr, msg):
    s.sendto(msg, addr)
    msg, address = s.recvfrom(4)
    return msg


def send_request(s, addr, msg):
    attempts = 0
    while True:
        try:
            msg = send_and_ack(s, addr, msg)
            ack = protocol.msg_number(msg)
            log.debug(f"ACK={ack}, SEQ_NUM={constant.CONN_START_SEQNUM}")
            if ack == constant.CONN_START_SEQNUM + 1:
                return msg

        except TimeoutError:
            attempts += 1
            if attempts >= constant.RETRY_NUMBER:
                log.error("Couldn't connect with server")
                sys.exit(1)


def upload(server_address, src, name):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(constant.CONNECTION_TIMEOUT)

    log.debug(
        f"Sending first message to {server_address[0]}:{server_address[1]}"
    )
    request = protocol.compose_request_msg(constant.UPLOAD, name)
    msg = send_request(s, server_address, request)
    log.debug(f"First Message sent to {server_address[0]}:{server_address[1]}")

    sender = protocol.Sender(src)

    while True:
        try:
            responses = sender.respond_to(msg)

            for resp in responses:
                s.sendto(resp, server_address)

            address = tuple()
            while address != server_address:
                try:
                    msg, address = s.recvfrom(constant.MAX_PKT_SIZE)
                except TimeoutError:
                    for resp in sender.timeout_response():
                        s.sendto(resp, server_address)

        except TimeoutError:
            log.error("Connection with server was lost")
            sys.exit(1)
        except StopIteration:
            break


def set_logging_level(quiet, verbose):
    verbosity = log.INFO
    if quiet:
        verbosity = log.ERROR
    elif verbose:
        verbosity = log.DEBUG

    log.basicConfig(
        level=verbosity,
        format="[%(asctime)s.%(msecs)03d] %(levelname)s"
        " - Upload: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    p = parser.upload_parser()
    args = p.parse_args()
    host = args.host
    port = args.port
    quiet = args.quiet
    verbose = args.verbose
    src = path.expanduser(args.src)
    name = args.name

    set_logging_level(quiet, verbose)

    upload((host, port), src, name)


if __name__ == "__main__":
    main()
