import logging as log
import socket
import sys
from os import path

from lib import constant, parser, protocol


def send_and_ack(s, msg, address):
    s.sendto(msg, address)
    msg, address = s.recvfrom(constant.MAX_PKT_SIZE)
    return msg


def send_request(s, msg, address):
    attempts = 0
    while True:
        try:
            msg = send_and_ack(s, msg, address)
            ack = protocol.msg_number(msg)
            log.debug(f"ack {ack}, iseqnum {constant.CONN_START_SEQNUM}")
            if ack == constant.CONN_START_SEQNUM + 1:
                return msg

        except TimeoutError:
            attempts += 1
            if attempts >= constant.RETRY_NUMBER:
                raise


def set_logging_level(quiet, verbose):
    log.basicConfig(level=log.INFO)
    if quiet:
        log.basicConfig(level=log.ERROR, force=True)
    if verbose:
        log.basicConfig(level=log.DEBUG, force=True)


def download():
    p = parser.download_parser()
    args = p.parse_args()
    host = args.host
    port = args.port
    quiet = args.quiet
    verbose = args.verbose
    dst = path.expanduser(args.dst)
    name = args.name

    set_logging_level(quiet, verbose)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(constant.RETRY_DELAY)

    log.info(f"Server Address: {host}:{port}")
    log.debug(f"Sending first message to {(host, port)}")
    request = protocol.compose_request_msg(constant.DOWNLOAD, name)
    msg = send_request(s, request, (host, port))
    log.debug(f"First Message sent to {(host, port)}")

    receiver = protocol.Receiver(dst)

    while True:
        try:
            responses = receiver.respond_to(msg)

            for resp in responses:
                s.sendto(resp, (host, port))

            try:
                address = tuple()
                while address != (host, port):
                    msg, address = s.recvfrom(constant.MAX_PKT_SIZE)

            except TimeoutError:
                for resp in receiver.timeout_response():
                    s.sendto(resp, (host, port))

        except TimeoutError:
            log.error("Connection with server was lost")
            sys.exit(1)
        except StopIteration:
            break


if __name__ == "__main__":
    download()
