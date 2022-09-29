import pytest
import random
from helpers import utils, process

port = random.randint(49152, 65535)


def download(size):
    global port
    port += 1
    src_file, dst_file = utils.create_test_files(size)
    _ = process.Server(utils.TMP_DIR, port)
    client = process.Download(dst_file.path, src_file.name, port)
    client.wait()
    return src_file.diff(dst_file)


@pytest.mark.parametrize("s", [0, 1, 1000, 4092])
def test_download_small(s):
    assert download(s) == 0


def test_download_medium():
    assert download(500_000) == 0


def test_download_big():
    assert download(10_000_000) == 0
