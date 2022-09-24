import subprocess
import tempfile
import os

# pytest tests
# pytest tests -s
PYTHON = 'python3'
SERVER = 'src/start-server-saw.py'
CLIENT = 'src/stop-and-wait/client-stop-and-wait.py'
SERVER_IS_UP = 'Socket binded to'


def run_server():
    return subprocess.Popen([PYTHON, '-u', SERVER, '-o', '-v'],
                            stdout=subprocess.PIPE,
                            bufsize=0,
                            close_fds=True,
                            universal_newlines=True)


def run_client(src, name):
    return subprocess.Popen([PYTHON, '-u', CLIENT, '-s', src, '-n', name],
                            stdout=subprocess.PIPE,
                            bufsize=0,
                            close_fds=True,
                            universal_newlines=True)


def diff(file1, file2):
    return subprocess.Popen(['diff', file1, file2])


def send(file1, file2):
    sproc = run_server()
    for line in iter(sproc.stdout.readline, ""):
        if line.startswith(SERVER_IS_UP):
            break
    run_client(file1, file2)
    sproc.wait()


def create_tmp_file(size):
    tmp = tempfile.NamedTemporaryFile(delete=False, mode="wb")
    tmp.write(os.urandom(size))
    tmp.close()
    return tmp.name


def create_empty_tmp_file():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    return tmp.name


def create_and_send(size):
    file1 = create_tmp_file(size)
    file2 = create_empty_tmp_file()
    send(file1, file2)
    status = diff(file1, file2).wait()
    os.unlink(file1)
    os.unlink(file2)
    return status


def test_send_small():
    assert create_and_send(30) == 0


def test_send_medium():
    assert create_and_send(10000) == 0


def test_send_big():
    assert create_and_send(100000) == 0
