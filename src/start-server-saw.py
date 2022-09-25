import logging as log
import socket
import sys
import threading
from os import path
from parser import parser as p

import lib.constant as constant
import lib.protocol as protocol


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


def check_timed_out_connections(connections, s):
    timed_out = [(a, c) for a, c in connections.items() if c.timed_out()]
    for addr, conn in timed_out:
        try:
            log.info(f"Connection {addr[0]}:{addr[1]} timed out")
            responses = conn.timeout_response()

            if len(responses) != 0:
                for resp in responses:
                    s.sendto(resp, addr)

        except TimeoutError:
            log.info(
                f"Connection {addr[0]}:{addr[1]} was closed due to timeout"
            )
            del connections[addr]


def recvfrom_timeout(connections, s, size):
    while True:
        try:
            msg, address = s.recvfrom(4096)
            return msg, address

        except socket.timeout:
            check_timed_out_connections(connections, s)


def recv_msg(connections, s, sdir, one_run):
    msg, address = recvfrom_timeout(connections, s, 4096)
    log.info(f"Received a message from {address[0]}:{address[1]}")

    if address not in connections:
        connections[address] = protocol.Connection(msg, sdir)

    try:
        for resp in connections[address].respond_to(msg):
            s.sendto(resp, address)
        return False

    except StopIteration:
        del connections[address]
        log.debug(f"Connection with {address[0]}:{address[1]} finished")
        return one_run


def main():
    parser = p.server_parser()
    args = parser.parse_args()
    host = args.host
    port = args.port
    quiet = args.quiet
    verbose = args.verbose
    sdir = path.expanduser(args.storage)
    one_run = args.one

    reading_thread = None
    if not one_run:
        reading_thread = threading.Thread(target=wait_for_q, daemon=True)
        reading_thread.start()

    connections = {}

    set_logging_level(quiet, verbose)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(constant.SOCKET_TIMEOUT)
        s.bind((host, port))
        print(f"Socket binded to port {port}")

        while True:
            if reading_thread and not reading_thread.is_alive():
                break

            check_timed_out_connections(connections, s)

            try:
                ended = recv_msg(connections, s, sdir, one_run)
                if ended:
                    break
            except TimeoutError:
                continue

    if reading_thread:
        reading_thread.join()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
