import logging as log
import socket
from parser import parser as p


def set_logging_level(quiet, verbose):
    log.basicConfig(level=log.INFO)
    if quiet:
        log.basicConfig(level=log.ERROR)
    if verbose:
        log.basicConfig(level=log.DEBUG)


def main():
    parser = p.server_parser()
    args = parser.parse_args()
    host = args.host
    port = args.port
    quiet = args.quiet
    verbose = args.verbose
    # sdir = args.storage

    set_logging_level(quiet, verbose)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        log.debug(f"Socket binded to {(host, port)}")

        while True:
            data, address = s.recvfrom(1024)
            log.info(f"Received from {address}")
            print(data.decode())


if __name__ == "__main__":
    main()
