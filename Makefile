
VENV_NAME="venv"

.PHONY = check
check: venv linter Makefile
	@echo "==> make check DONE"

venv: .built-venv

.built-venv: requirements.txt
	( \
		python3 -m venv ${VENV_NAME}; \
		. ${VENV_NAME}/bin/activate; \
		pip install --upgrade pip; \
		pip install -r requirements.txt; \
		touch $@;\
	)

.built-linter: venv requirements.txt
	@(\
	. venv/bin/activate; \
	echo "=============== FLAKE8 ========================="; \
	python -m flake8 --max-line-length 120 roon_remote.py; \
	echo -e "==> FLAKE8 is Done\n"; \
	echo "=============== PYLINT ========================="; \
	python -m pylint roon_remote.py; \
	echo "==> PYLINT is Done"; \
	)

linter: .built-linter

clean:
	rm -f .built-*
	rm -rf ${VENV_NAME}
