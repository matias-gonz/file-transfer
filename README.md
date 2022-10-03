# file-transfer
[![Tests](https://github.com/matias-gonz/file-transfer/actions/workflows/tests.yml/badge.svg)](https://github.com/matias-gonz/file-transfer/actions/workflows/tests.yml)
[![Linter](https://github.com/matias-gonz/file-transfer/actions/workflows/linter.yml/badge.svg?branch=main)](https://github.com/matias-gonz/file-transfer/actions/workflows/linter.yml)

## Installation

### Dependencies:
* [python3.10^](https://www.python.org/downloads/)
* [Poetry](https://python-poetry.org/docs/#installation)

Once you have installed these tools, make will take care of the rest :relieved:

``` bash
$ make install
```

## Usage

### Start the server
``` bash
$ project_root/src/start-server.py
```

For help using the command, use the option `--help`:

``` bash
$ project_root/src/start-server.py --help
usage: start-server.py [-h] [-v | -q] [-H HOST] [-p PORT] [-s STORAGE] [-o] [-w WINDOW]

Starts file-sharing server

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -q, --quiet           decrease output verbosity
  -H HOST, --host HOST  service IP address
  -p PORT, --port PORT  service port
  -s STORAGE, --storage STORAGE
                        storage dir path
  -o, --one             only one transfer
  -w WINDOW, --window WINDOW
                        size of the sending window
```

### Start an upload
``` bash
$ project_root/src/upload.py
```

For help using the command, use the option `--help`:

``` bash
$ project_root/src/upload.py --help
usage: upload.py [-h] [-v | -q] [-H HOST] [-p PORT] [-s SRC] [-n NAME] [-w WINDOW]

Uploads a file to the file-sharing server

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -q, --quiet           decrease output verbosity
  -H HOST, --host HOST  server IP address
  -p PORT, --port PORT  server port
  -s SRC, --src SRC     source file path
  -n NAME, --name NAME  file name
  -w WINDOW, --window WINDOW
                        size of the sending window
```

### Start a download
``` bash
$ project_root/src/download.py
```

For help using the command, use the option `--help`:

``` bash
$ project_root/src/download.py --help
usage: download.py [-h] [-v | -q] [-H HOST] [-p PORT] [-d DST] [-n NAME]

Downloads a file from the file-sharing server

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -q, --quiet           decrease output verbosity
  -H HOST, --host HOST  server IP address
  -p PORT, --port PORT  server port
  -d DST, --dst DST     destination file path
  -n NAME, --name NAME  file name
```

## Run formatters and linter

The repository uses GitHub Workflows to run a linter on each push or pull request.
To run the automatic formatter and linter manually use the following command:

``` bash
$ make lint
```
