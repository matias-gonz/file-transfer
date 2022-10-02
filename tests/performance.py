#!/usr/bin/env python3
from helpers import process, utils
import timeit
import random


SAW_WINDOW = 1
GBN_WINDOW = 10
NUMBER_OF_TIMES = 2

KB = 1024
MB = 1024 ** 2


def start_server(ws, port):
    return process.Server(utils.TMP_DIR, port, False, ws, quiet=True)


def get_next_port():
    return random.randint(1024, 65535)


def upload(size, ws):
    port = get_next_port()
    src, dst = utils.create_test_files(size)
    server = start_server(ws, port)
    client = process.Upload(src.path, dst.name, port, ws, quiet=True)
    status = client.wait()
    server.kill()
    assert status == 0


def upload_saw(size):
    upload(size, SAW_WINDOW)


def upload_gbn(size):
    upload(size, GBN_WINDOW)


def download(size, ws):
    port = get_next_port()
    src, dst = utils.create_test_files(size)
    server = start_server(ws, port)
    client = process.Download(dst.path, src.name, port, quiet=True)
    status = client.wait()
    server.kill()
    assert status == 0


def download_saw(size):
    download(size, SAW_WINDOW)


def download_gbn(size):
    download(size, GBN_WINDOW)


def calculate_timelapse(fun, number):
    t1 = timeit.default_timer()
    for i in range(number):
        fun()
    t2 = timeit.default_timer()
    return (t2 - t1) / number


def time_all(size):
    results = []
    for f in (upload_saw, upload_gbn, download_saw, download_gbn):
        results.append(calculate_timelapse(lambda: f(size), NUMBER_OF_TIMES))
    return tuple(results)


def main():
    for size in (1, 2 * KB, 2 * MB):
        up_saw, up_gbn, dn_saw, dn_gbn = time_all(size)
        l_saw = len('  Stop-and-Wait  ') - 2
        l_gbn = len('   Go-Back-N   ') - 2
        print(f"Time taken for transferring a file of {size} Bytes")
        print(f"_________|  Stop-and-Wait  |   Go-Back-N   |   difference")
        print(f"Upload   | {up_saw:>{l_saw}.8g} | {up_gbn:>{l_gbn}.8g} |  {up_saw - up_gbn:#.8g}")
        print(f"Download | {dn_saw:>{l_saw}.8g} | {dn_gbn:>{l_gbn}.8g} |  {up_saw - up_gbn:#.8g}")
        print()


if __name__ == "__main__":
    main()
