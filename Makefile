
VENV_NAME="venv"

check: venv test_roon.api.py
	echo "make check"
	( \
		. ${VENV_NAME}/bin/activate; \
		python test_roon.api.py; \
	)

venv: .built-venv

.built-venv: requirements.txt
	( \
		python3 -m venv ${VENV_NAME}; \
		. ${VENV_NAME}/bin/activate; \
		pip install --upgrade pip; \
		pip install -r requirements.txt; \
		touch $@;\
	)

clean:
	rm -f .built-*
	rm -rf ${VENV_NAME}
