
VENV_NAME="venv"
TEST_SRC = $(shell find tests/ -type f -name '*.py')
APP_SRC = $(shell find app/ -type f -name '*.py')
APP_SRC += roon_remote.py

.PHONY = check
check: venv linter pytest Makefile
	@echo "==> make check DONE"

venv: .built-venv

pytest: .built-pytest

.built-pytest: ${TEST_SRC} ${APP_SRC}
	( \
	. ${VENV_NAME}/bin/activate; \
	python -m pytest -v tests/; \
	touch $@; \
	)

.built-venv: requirements.txt
	( \
		python3 -m venv ${VENV_NAME}; \
		. ${VENV_NAME}/bin/activate; \
		pip install --upgrade pip; \
		pip install -r requirements.txt; \
		touch $@;\
	)

.built-linter: venv requirements.txt ${APP_SRC}
	@(\
	. venv/bin/activate; \
	echo "=============== FLAKE8 ========================="; \
	python -m flake8 --max-line-length 120 roon_remote.py; \
	echo -e "==> FLAKE8 is Done\n"; \
	echo "=============== PYLINT ========================="; \
	python -m pylint roon_remote.py; \
	echo "==> PYLINT is Done"; \
	touch $@; \
	)

linter: .built-linter

clean:
	rm -f .built-*
	rm -rf ${VENV_NAME}
