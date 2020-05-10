VENV_BIN=$(CURDIR)/.venv/bin

.PHONY: tests run start_redis pull_redis

.venv:
	virtualenv --python python2.7 .venv
	$(VENV_BIN)/pip install -r requirements.txt

run: .venv
	$(VENV_BIN)/python src/api.py

tests: pull_redis
	cd src && $(VENV_BIN)/python -m unittest discover -s ../tests $(args)

start_redis:
	docker run --rm -p 127.0.0.1:6379:6379/tcp  redis:latest

pull_redis:
	docker pull redis:latest
