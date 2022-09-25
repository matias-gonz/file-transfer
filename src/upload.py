import logging as log
import socket
from parser import parser as p


def set_logging_level(quiet, verbose):
    log.basicConfig(level=log.INFO)
    if quiet:
        log.basicConfig(level=log.ERROR, force=True)
    if verbose:
        log.basicConfig(level=log.DEBUG, force=True)


def main():
    parser = p.upload_parser()
    args = parser.parse_args()
    host = args.host
    port = args.port
    quiet = args.quiet
    verbose = args.verbose
    # src = args.src
    # name = args.name

    set_logging_level(quiet, verbose)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        for i in range(5):
            s.sendto("I'm the client".encode(), (host, port))


if __name__ == "__main__":
    main()
