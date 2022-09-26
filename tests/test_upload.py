from helpers import utils, process


def upload(size):
    src_file, dst_file = utils.create_test_files(size)
    server = process.Server(utils.TMP_DIR)
    process.Upload(src_file.path, dst_file.name)
    server.wait()
    return src_file.diff(dst_file)


def test_upload_small():
    assert upload(30) == 0


def test_upload_medium():
    assert upload(10_000) == 0


def test_upload_big():
    assert upload(10_000_000) == 0
