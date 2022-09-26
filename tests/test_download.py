from helpers import utils, process


def download(size):
    src_file, dst_file = utils.create_test_files(size)
    _ = process.Server('/tmp')
    process.Download(dst_file.path, src_file.name)
    return src_file.diff(dst_file)


def test_download_small():
    assert download(30) == 0


def test_download_medium():
    assert download(10000) == 0


# def test_send_big():
#     assert download(10_000_000) == 0
