.PHONY: install install-db serve check lint fix format format-check pre-commit install-hooks compose-up compose-down clean

VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
UVICORN ?= $(PYTHON) -m uvicorn
PYTEST ?= $(PYTHON) -m pytest
PYTEST_ARGS ?= -vv -ra --cov=app --cov-report=term-missing --cov-fail-under=90
RUFF ?= $(PYTHON) -m ruff
APP ?= app.main:app
HOST ?= 0.0.0.0
PORT ?= 8000
REQ_DIR ?= requirements
REQ_IN ?= $(REQ_DIR)/requirements.in
REQ_LOCK ?= $(REQ_DIR)/requirements.lock

install: install-hooks
	@if [ ! -d $(VENV) ]; then uv venv $(VENV); fi
	uv pip compile $(REQ_IN) --generate-hashes -o $(REQ_LOCK)
	uv pip install --python $(PYTHON) -r $(REQ_LOCK)

install-hooks:
	@git config core.hooksPath .githooks
	@chmod +x .githooks/pre-commit
	@echo "Git hooks installed. pre-commit will run make pre-commit"

install-db:
	@if [ ! -d $(VENV) ]; then uv venv $(VENV); fi
	$(PYTHON) -c "from app.db import reset_db; reset_db()"

serve:
	$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

check:
	$(PYTEST) $(PYTEST_ARGS)

lint:
	$(RUFF) check .

fix:
	$(RUFF) check . --fix

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache $(REQ_LOCK)

format:
	$(RUFF) format .

pre-commit:
	$(MAKE) format
	$(MAKE) lint
	@git diff --quiet || (echo "Formatting changed files. Stage changes and commit again." && exit 1)

docker-run:
	docker compose up -d db

docker-stop:
	docker compose down
