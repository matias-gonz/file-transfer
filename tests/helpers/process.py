import os
import subprocess
import signal
from . import constant


class Process:
    def __init__(self, cmd):
        self.p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            bufsize=0,
            close_fds=True,
            universal_newlines=True,
            start_new_session=True
        )
        self.timeout_s = constant.TIMEOUT_S

    def wait(self):
        return self.p.wait()

    def kill(self):
        self.p.kill()

    def __del__(self):
        try:
            self.p.wait(timeout=self.timeout_s)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(self.p.pid), signal.SIGTERM)


class Server(Process):

    def __init__(self, storage_dir, port, onerun=True):
        cmd = [constant.PYTHON, '-u', constant.SERVER,
               '-v', '-s', storage_dir, '-p', str(port)]
        if onerun:
            cmd.append('-o')
        super().__init__(cmd)

        for line in iter(self.p.stdout.readline, ""):
            if line.startswith(constant.SERVER_IS_UP):
                break


class Upload(Process):

    def __init__(self, src_path, dst_name, port):
        cmd = [constant.PYTHON, '-u', constant.UPLOAD,
               '-v', '-s', src_path, '-n', dst_name, '-p', str(port)]
        super().__init__(cmd)


class Download(Process):

    def __init__(self, dst_path, src_name, port):
        cmd = [constant.PYTHON, '-u', constant.DOWNLOAD,
               '-v', '-d', dst_path, '-n', src_name, '-p', str(port)]
        super().__init__(cmd)
