POETRY=poetry
BLACK=$(POETRY) run black
ISORT=$(POETRY) run isort
FLAKE8=$(POETRY) run flake8
PYTEST=$(POETRY) run pytest
PACKAGE=src
TESTS=tests
LOSS=./loss.sh
SERVER=src/start-server.py
UPLOAD=src/upload.py
DOWNLOAD=src/download.py

install:
	$(POETRY) install
	$(POETRY_EXPORT)
	chmod u+x ${SERVER} ${UPLOAD} ${DOWNLOAD}

fmt:
	$(ISORT) ./${PACKAGE}
	$(BLACK) ./${PACKAGE} --line-length 79

lint: fmt
	$(FLAKE8) ./${PACKAGE}

test:
	$(PYTEST) ./${TESTS}

loss-up:
	$(LOSS) up

loss-down:
	$(LOSS) down

test-loss : loss-up test loss-down

all: lint test
