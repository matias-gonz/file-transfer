import tempfile

from helpers import utils, process


def download(size):
    src_file, dst_file = utils.create_test_files(size)
    _ = process.Server(utils.TMP_DIR)
    client = process.Download(dst_file.path, src_file.name)
    client.wait()
    return src_file.diff(dst_file)


def test_download_small():
    assert download(30) == 0


def test_download_medium():
    assert download(10_000) == 0


def test_download_big():
    assert download(10_000_000) == 0
