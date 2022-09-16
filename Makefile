POETRY=poetry
BLACK=$(POETRY) run black
ISORT=$(POETRY) run isort
FLAKE8=$(POETRY) run flake8
PACKAGE=src

install:
	$(POETRY) install
	$(POETRY_EXPORT)

fmt:
	$(ISORT) ./${PACKAGE}
	$(BLACK) ./${PACKAGE}

lint: fmt
	$(FLAKE8) ./${PACKAGE}

server:
	$ python3 ./src/server.py

client:
	$ python3 ./src/client.py
