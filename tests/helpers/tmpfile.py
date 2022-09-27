import tempfile
import os
import subprocess


TMP_DIR = tempfile.gettempdir()


class TmpFile:
    def __init__(self, path):
        self.path = path
        self.name = self.path[len(tempfile.gettempdir()) + 1:]

    def diff(self, f):
        return subprocess.Popen(['diff', self.path, f.path]).wait()

    def __del__(self):
        os.unlink(self.path)


class SizedTmpFile(TmpFile):
    def __init__(self, size):
        tmp = tempfile.NamedTemporaryFile(delete=False, mode="wb")
        blk_size = 4096
        for i in range(0, size - blk_size, blk_size):
            tmp.write(os.urandom(blk_size))
        tmp.write(os.urandom(size % blk_size))
        tmp.close()
        super().__init__(tmp.name)


class EmptyTmpFile(TmpFile):
    def __init__(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        super().__init__(tmp.name)
