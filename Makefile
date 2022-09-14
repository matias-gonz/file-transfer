POETRY=poetry
BLACK=$(POETRY) run black
ISORT=$(POETRY) run isort
PYLINT=$(POETRY) run pylint
PACKAGE=src

install:
	$(POETRY) install
	$(POETRY_EXPORT)

fmt:
	$(ISORT) ./${PACKAGE}
	$(BLACK) ./${PACKAGE}

lint: fmt
	$(PYLINT) ./${PACKAGE}

server:
	$ python3 ./src/server.py

client:
	$ python3 ./src/client.py
