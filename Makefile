VENV_BIN=$(CURDIR)/.venv/bin

.PHONY: tests run

.venv:
	virtualenv --python python2.7 .venv
	$(VENV_BIN)/pip install -r requirements.txt

run:
	$(VENV_BIN)/python src/api.py

tests:
	cd src && $(VENV_BIN)/python -m unittest discover -s ../tests $(args)
