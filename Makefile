POETRY=poetry
BLACK=$(POETRY) run black
ISORT=$(POETRY) run isort
FLAKE8=$(POETRY) run flake8
PYTEST=$(POETRY) run pytest
PACKAGE=src
TESTS=tests

install:
	$(POETRY) install
	$(POETRY_EXPORT)

fmt:
	$(ISORT) ./${PACKAGE}
	$(BLACK) ./${PACKAGE} --line-length 79

lint: fmt
	$(FLAKE8) ./${PACKAGE}

test:
	$(PYTEST) ./${TESTS}

all: lint test
