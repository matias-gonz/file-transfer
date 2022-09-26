import logging as log
import socket
import sys
import threading
from os import path

from lib import constant, parser, protocol


def check_timed_out_connections(connections, s):
    timed_out = [(a, c) for a, c in connections.items() if c.timed_out()]
    for addr, conn in timed_out:
        try:
            responses = conn.timeout_response()

            log.info(f"Connection {addr[0]}:{addr[1]} timed out")

            for resp in responses:
                s.sendto(resp, addr)

        except TimeoutError:
            log.info(
                f"Connection {addr[0]}:{addr[1]} was closed due to timeout"
            )
            del connections[addr]
        except StopIteration:
            log.info(f"Connection {addr[0]}:{addr[1]} finished by timeout")
            del connections[addr]


def recv_msg(connections, s, sdir, one_run):
    msg, address = s.recvfrom(constant.MAX_PKT_SIZE)
    h = address[0]
    p = address[1]

    log.info(f"Received a message from {h}:{p} with size {len(msg)}")

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
        log.debug(f"Connection with {h}:{p} finished")
        return one_run


def wait_for_q():
    log.info("Ingrese 'q' para finalizar...")
    try:
        while input() != "q":
            pass
    except EOFError:
        pass


def set_logging_level(quiet, verbose):
    verbosity = log.INFO
    if quiet:
        verbosity = log.ERROR
    elif verbose:
        verbosity = log.DEBUG

    log.basicConfig(
        level=verbosity,
        format="[%(asctime)s.%(msecs)03d] %(levelname)s - Server: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    p = parser.server_parser()
    args = p.parse_args()
    host = args.host
    port = args.port
    quiet = args.quiet
    verbose = args.verbose
    sdir = path.expanduser(args.storage) + "/"
    one_run = args.one

    set_logging_level(quiet, verbose)

    reading_thread = None
    if not one_run:
        reading_thread = threading.Thread(target=wait_for_q, daemon=True)
        reading_thread.start()

    connections = {}

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(constant.SOCKET_TIMEOUT)
        s.bind((host, port))
        if not quiet:
            print(f"Socket bound to port {port}")

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
