import logging as log
import socket
import sys
from os import path

from lib import constant, parser, protocol


def send_and_recv(s, addr, msg):
    s.sendto(msg, addr)
    attempts = 0
    while True:
        try:
            return s.recvfrom(constant.MAX_PKT_SIZE)[0]
        except TimeoutError:
            attempts += 1
            if attempts >= constant.RETRY_NUMBER:
                log.error("Couldn't connect with server")
                sys.exit(1)


def send_request(s, addr, msg):
    while True:
        msg_recvd = send_and_recv(s, addr, msg)
        seq_num = protocol.msg_number(msg_recvd)
        log.debug(
            f"SEQ_NUM={seq_num}, EXPECTED={constant.CONN_START_SEQNUM}"
        )
        if seq_num == constant.CONN_START_SEQNUM:
            response_code = protocol.msg_response_code(msg_recvd)

            if response_code != constant.ALL_OK:
                log.error(f"The server returned a response code of {response_code}")
                sys.exit(2 + response_code)

            return send_and_recv(s, addr, protocol.compose_msg(1))


def set_logging_level(quiet, verbose):
    verbosity = log.INFO
    if quiet:
        verbosity = log.ERROR
    elif verbose:
        verbosity = log.DEBUG

    log.basicConfig(
        level=verbosity,
        format="[%(asctime)s.%(msecs)03d] %(levelname)s"
        " - Download: %(message)s",
        datefmt="%H:%M:%S",
    )


def download(server_address, dst, name):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(constant.CONNECTION_TIMEOUT)

    log.debug(
        f"Sending first message to {server_address[0]}:{server_address[1]}"
    )
    request = protocol.compose_request_msg(constant.DOWNLOAD, name)
    msg = send_request(s, server_address, request)
    log.debug(f"First message sent to {server_address[0]}:{server_address[1]}")

    try:
        log.debug(f"Writing to file: '{dst}'")
        with open(dst, "wb") as f:
            protocol.handle_clientside_conn(
                s, server_address, protocol.Receiver(f), msg
            )
    except TimeoutError:
        log.error("Connection with server was lost")
        sys.exit(1)
    except OSError:
        log.error("Couldn't open file for write")
        sys.exit(2)


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

    download((host, port), dst, name)


if __name__ == "__main__":
    main()
