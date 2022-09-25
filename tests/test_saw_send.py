import subprocess
import tempfile
import os


PYTHON = 'python3'
SERVER = 'src/start-server-saw.py'
CLIENT = 'src/stop-and-wait/client-stop-and-wait.py'
SERVER_IS_UP = 'Socket binded to'


def run(cmd):
    return subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            bufsize=0,
                            close_fds=True,
                            universal_newlines=True)


def run_server(storage_dir):
    cmd = [PYTHON, '-u', SERVER, '-o', '-v', '-s', storage_dir]
    return run(cmd)


def run_client(src, name):
    cmd = [PYTHON, '-u', CLIENT, '-v', '-s', src, '-n', name]
    return run(cmd)


def diff(file1, file2):
    return subprocess.Popen(['diff', file1, file2])


def send(file1, filename2):
    sproc = run_server('/tmp')
    for line in iter(sproc.stdout.readline, ""):
        if line.startswith(SERVER_IS_UP):
            break
    run_client(file1, filename2)
    sproc.wait()


def create_tmp_file(size):
    tmp = tempfile.NamedTemporaryFile(delete=False, mode="wb")
    tmp.write(os.urandom(size))
    tmp.close()
    return tmp.name


def create_empty_tmp_file():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    return tmp.name, tmp.name[len('/tmp/'):]


def create_and_send(size):
    file1 = create_tmp_file(size)
    file2, filename2 = create_empty_tmp_file()
    send(file1, filename2)
    status = diff(file1, file2).wait()
    os.unlink(file1)
    os.unlink(file2)
    return status


def test_send_small():
    assert create_and_send(30) == 0


def test_send_medium():
    assert create_and_send(10000) == 0


def test_send_big():
    assert create_and_send(500000) == 0
