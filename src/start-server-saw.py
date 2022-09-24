import logging as log
import socket
from parser import parser as p

from lib.protocol import Connection


def set_logging_level(quiet, verbose):
    log.basicConfig(level=log.INFO)
    if quiet:
        log.basicConfig(level=log.ERROR, force=True)
    if verbose:
        log.basicConfig(level=log.DEBUG, force=True)


def main():
    parser = p.server_parser()
    args = parser.parse_args()
    host = args.host
    port = args.port
    quiet = args.quiet
    verbose = args.verbose

    connections = {}

    set_logging_level(quiet, verbose)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        print(f"Socket binded to {(host, port)}")

        while True:
            msg, address = s.recvfrom(4096)
            log.info(f"Received from {address}")

            if address not in connections:
                connections[address] = Connection(address, msg)

            response = connections[address].respond_to(msg)

            if len(response) == 0:
                del connections[address]
                if args.one:
                    break
            else:
                s.sendto(response, address)


if __name__ == "__main__":
    main()
