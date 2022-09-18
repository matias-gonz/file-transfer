import argparse

LOCAL_HOST = "127.0.0.1"
DEFAULT_PORT = 6543
DEFAULT_DIR_PATH = "~"

p = argparse.ArgumentParser()

log_group = p.add_mutually_exclusive_group()
log_group.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="increase output verbosity",
)
log_group.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help=" decrease output verbosity",
)
p.add_argument(
    "-H",
    "--host",
    default=LOCAL_HOST,
    help="service IP address",
)
p.add_argument(
    "-p",
    "--port",
    type=int,
    default=DEFAULT_PORT,
    help="service port",
)


def server_parser():
    p.add_argument(
        "-s",
        "--storage",
        default=DEFAULT_DIR_PATH,
        help="storage dir path",
    )
    return p


def upload_parser():
    p.add_argument(
        "-s",
        "--src",
        default=DEFAULT_DIR_PATH,
        help="source file path",
    )
    p.add_argument(
        "-n",
        "--name",
        help="file name",
    )
    return p


def download_parser():
    p.add_argument(
        "-d",
        "--dst",
        default=DEFAULT_DIR_PATH,
        help="destination file path",
    )
    p.add_argument(
        "-n",
        "--name",
        help="file name",
    )
    return p
