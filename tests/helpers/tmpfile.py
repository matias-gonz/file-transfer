import tempfile
import os
import subprocess


class TmpFile:
    def __init__(self, path):
        self.path = path
        self.name = self.path[len('/tmp/'):]

    def diff(self, f):
        return subprocess.Popen(['diff', self.path, f.path]).wait()

    def __del__(self):
        os.unlink(self.path)


class SizedTmpFile(TmpFile):
    def __init__(self, size):
        tmp = tempfile.NamedTemporaryFile(delete=False, mode="wb")
        for i in range(0, size, 4096):
            tmp.write(os.urandom(4096))
        tmp.close()
        super().__init__(tmp.name)


class EmptyTmpFile(TmpFile):
    def __init__(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        super().__init__(tmp.name)
