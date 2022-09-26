from helpers import utils, process


def upload(size):
    src_file, dst_file = utils.create_test_files(size)
    _ = process.Server('/tmp')
    process.Upload(src_file.path, dst_file.name)
    return src_file.diff(dst_file)


def test_upload_small():
    assert upload(30) == 0


def test_upload_medium():
    assert upload(10000) == 0


def test_upload_big():
    assert upload(10_000_000) == 0