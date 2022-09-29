import pytest
import random
from helpers import utils, process

port = random.randint(49152, 65535)

def upload(size):
    global port
    port += 1
    src_file, dst_file = utils.create_test_files(size)
    server = process.Server(utils.TMP_DIR, port)
    _ = process.Upload(src_file.path, dst_file.name, port)
    server.wait()
    return src_file.diff(dst_file)


@pytest.mark.parametrize("s", [0, 1, 1000, 4092])
def test_upload_small(s):
    assert upload(s) == 0


def test_upload_medium():
    assert upload(500_000) == 0


def test_upload_big():
    assert upload(2_000_000) == 0
