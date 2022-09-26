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
    verbosity = log.INFO
    if quiet:
        verbosity = log.ERROR
    elif verbose:
        verbosity = log.DEBUG

    log.basicConfig(
        level=verbosity,
        format="[%(asctime)s.%(msecs)03d] %(levelname)s"
        "- Download: %(message)s",
        datefmt="%H:%M:%S",
    )


def download(host, port, dst, name):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(constant.SOCKET_TIMEOUT)

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


def main():
    p = parser.download_parser()
    args = p.parse_args()
    host = args.host
    port = args.port
    quiet = args.quiet
    verbose = args.verbose
    dst = path.expanduser(args.dst)
    name = args.name

    set_logging_level(quiet, verbose)

    download(host, port, dst, name)


if __name__ == "__main__":
    main()
