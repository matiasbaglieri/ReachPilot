VENV_NAME = venv
PYTHON = python3
PIP = pip3

.PHONY: venv install clean run run-matias run-fran env

venv:
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "Virtual environment created. Activate it with 'source venv/bin/activate'"

env:
	source venv/bin/activate
	
install: venv
	. $(VENV_NAME)/bin/activate && $(PIP) install -r requirements.txt
	@echo "Dependencies installed in virtual environment"

run-matias: install
	cp .env-matias .env
	. $(VENV_NAME)/bin/activate && $(PYTHON) main.py

run-fran: install
	cp .env-fran .env
	. $(VENV_NAME)/bin/activate && $(PYTHON) main.py

run-local: install
	cp .env-local .env
	. $(VENV_NAME)/bin/activate && $(PYTHON) main.py

run: run-local

clean:
	rm -rf $(VENV_NAME)
	@echo "Virtual environment removed"