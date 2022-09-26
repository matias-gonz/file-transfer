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
	$(BLACK) ./${PACKAGE} --line-length 79

lint: fmt
	$(FLAKE8) ./${PACKAGE}

server:
	$ python3 ./src/server.py

client:
	$ python3 ./src/client.py

server-saw:
	$ python3 ./src/start-server-saw.py -s 'Hola'

upload-saw:
	$ python3 ./src/upload-saw.py

test:
	$ $(POETRY) run pytest ./tests
