import logging as log
import socket
import sys
import threading
from os import path
from parser import parser as p

from lib import constant, protocol


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

            for resp in responses:
                s.sendto(resp, addr)

        except TimeoutError:
            log.info(
                f"Connection {addr[0]}:{addr[1]} was closed due to timeout"
            )
            del connections[addr]


def recv_msg(connections, s, sdir, one_run):

    msg, address = s.recvfrom(constant.MAX_PKT_SIZE)

    log.info(f"Received a message from {address[0]}:{address[1]} with size {len(msg)}")

    if address not in connections:
        try:
            connections[address] = protocol.Connection(msg, sdir)
        except ValueError:
            return False

    try:
        for resp in connections[address].respond_to(msg):
            s.sendto(resp, address)

        if connections[address].finished():
            raise StopIteration()

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
    sdir = path.expanduser(args.storage) + "/"
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

            try:
                check_timed_out_connections(connections, s)
                ended = recv_msg(connections, s, sdir, one_run)
                if ended:
                    break
            except TimeoutError:
                continue
            except StopIteration:
                continue

    if reading_thread:
        reading_thread.join()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
