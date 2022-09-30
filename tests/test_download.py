import pytest
import random
from helpers import utils, process
import tempfile

port = random.randint(49152, 65535)


def download(size):
    global port
    port += 1
    src_file, dst_file = utils.create_test_files(size)
    _ = process.Server(utils.TMP_DIR, port)
    client = process.Download(dst_file.path, src_file.name, port)
    client.wait()
    return src_file.diff(dst_file)


def test_download_nonexistent_file():
    global port
    port += 1
    _, dst_file = utils.create_test_files(1)
    with tempfile.TemporaryDirectory() as dir_name:
        server = process.Server(dir_name, port, False)
        client = process.Download(dst_file.path, "nonexistent", port)
        status = client.wait()
        server.kill()
        assert status == 3  # server file open error


@pytest.mark.parametrize("s", [0, 1, 1000, 4092])
def test_download_small(s):
    assert download(s) == 0


def test_download_medium():
    assert download(500_000) == 0


def test_download_big():
    assert download(2_000_000) == 0
