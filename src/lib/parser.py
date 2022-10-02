import argparse

LOCAL_HOST = "127.0.0.1"
DEFAULT_PORT = 6543
DEFAULT_DIR_PATH = "~"
DEFAULT_FILE_PATH = "~/prueba.txt"
DEFAULT_FILE_NAME = "a.out"
DEFAULT_WINDOW = 10


def add_common_options(parser):
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
        help="decrease output verbosity",
    )


def server_parser():
    parser = argparse.ArgumentParser(
        description="Starts file-sharing server",
    )
    add_common_options(parser)
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
    parser.add_argument(
        "-o",
        "--one",
        action="store_true",
        help="only one transfer",
    )
    parser.add_argument(
        "-w",
        "--window",
        type=int,
        default=DEFAULT_WINDOW,
        help="size of the sending window",
    )
    return parser


def upload_parser():
    parser = argparse.ArgumentParser(
        description="Uploads a file to the file-sharing server",
    )
    add_common_options(parser)
    parser.add_argument(
        "-H",
        "--host",
        default=LOCAL_HOST,
        help="server IP address",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="server port",
    )
    parser.add_argument(
        "-s",
        "--src",
        default=DEFAULT_FILE_PATH,
        help="source file path",
    )
    parser.add_argument(
        "-n",
        "--name",
        default=DEFAULT_FILE_NAME,
        help="file name",
    )
    parser.add_argument(
        "-w",
        "--window",
        type=int,
        default=DEFAULT_WINDOW,
        help="size of the sending window",
    )
    return parser


def download_parser():
    parser = argparse.ArgumentParser(
        description="Downloads a file from the file-sharing server",
    )
    add_common_options(parser)
    parser.add_argument(
        "-H",
        "--host",
        default=LOCAL_HOST,
        help="server IP address",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="server port",
    )
    parser.add_argument(
        "-d",
        "--dst",
        default=DEFAULT_FILE_PATH,
        help="destination file path",
    )
    parser.add_argument(
        "-n",
        "--name",
        help="file name",
        default=DEFAULT_FILE_NAME,
    )
    return parser
