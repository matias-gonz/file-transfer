from helpers import tmpfile


def create_test_files(size):
    return tmpfile.SizedTmpFile(size), tmpfile.EmptyTmpFile()
