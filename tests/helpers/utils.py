from . import tmpfile


TMP_DIR = tmpfile.TMP_DIR


def create_test_files(size):
    return tmpfile.SizedTmpFile(size), tmpfile.EmptyTmpFile()
