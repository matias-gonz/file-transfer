import threading
import logging as log
import socket
from parser import parser as p

from lib.protocol import Connection

TIMEOUT = 0.100  # 100 ms


def set_logging_level(quiet, verbose):
    log.basicConfig(level=log.INFO)
    if quiet:
        log.basicConfig(level=log.ERROR, force=True)
    if verbose:
        log.basicConfig(level=log.DEBUG, force=True)


def wait_for_q():
    print("Ingrese 'q' para finalizar...")
    try:
        while input() != "q":
            pass
    except EOFError:
        pass


def main():
    parser = p.server_parser()
    args = parser.parse_args()
    host = args.host
    port = args.port
    quiet = args.quiet
    verbose = args.verbose
    sdir = args.storage

    reading_thread = threading.Thread(target=wait_for_q)
    reading_thread.start()

    connections = {}

    set_logging_level(quiet, verbose)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(TIMEOUT)
        s.bind((host, port))
        log.debug(f"Socket binded to port {port}")

        while True:
            if not reading_thread.is_alive():
                break

            try:
                msg, address = s.recvfrom(4096)
            except TimeoutError:
                # log.debug("Timeout")
                continue

            log.info(f"Received a message from {address[0]}:{address[1]}")

            if address not in connections:
                connections[address] = Connection(address, msg)

            response = connections[address].respond_to(msg)

            if len(response) == 0:
                del connections[address]
                log.debug(f"Connection with {address[0]}:{address[1]} finished")
            else:
                s.sendto(response, address)

    reading_thread.join()


if __name__ == "__main__":
    main()
