.PHONY: install install-db serve check lint format clean

VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
UVICORN ?= $(VENV)/bin/uvicorn
PYTEST ?= $(VENV)/bin/pytest
PYTEST_ARGS ?= -vv -ra --cov=app --cov-report=term-missing --cov-fail-under=90
RUFF ?= $(VENV)/bin/ruff
APP ?= app.main:app
HOST ?= 0.0.0.0
PORT ?= 8000
REQ_DIR ?= requirements
REQ_IN ?= $(REQ_DIR)/requirements.in
REQ_LOCK ?= $(REQ_DIR)/requirements.lock

install:
	@if [ ! -d $(VENV) ]; then uv venv $(VENV); fi
	uv pip compile $(REQ_IN) --generate-hashes -o $(REQ_LOCK)
	uv pip install --python $(PYTHON) -r $(REQ_LOCK)

install-db:
	@if [ ! -d $(VENV) ]; then uv venv $(VENV); fi
	$(PYTHON) -c "from app.db import reset_db; reset_db()"

serve:
	$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

check:
	$(PYTEST) $(PYTEST_ARGS)

lint:
	$(RUFF) check .

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache $(REQ_LOCK)

format:
	$(RUFF) format .
