import argparse

LOCAL_HOST = "127.0.0.1"
DEFAULT_PORT = 6543
DEFAULT_DIR_PATH = "~"

parser = argparse.ArgumentParser()

log_group = parser.add_mutually_exclusive_group()
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
parser.add_argument(
    "-H",
    "--host",
    default=LOCAL_HOST,
    help="service IP address",
)
parser.add_argument(
    "-p",
    "--port",
    type=int,
    default=DEFAULT_PORT,
    help="service port",
)
parser.add_argument(
    "-s",
    "--storage",
    default=DEFAULT_DIR_PATH,
    help="storage dir path",
)
