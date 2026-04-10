.PHONY: install install-db serve check check-unit check-integration lint fix format format-check pre-commit install-hooks compose-up compose-down clean upgrade audit

VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
UVICORN ?= $(PYTHON) -m uvicorn
PYTEST ?= $(PYTHON) -m pytest
PYTEST_ARGS ?= -vv -ra --cov=app --cov-report=term-missing --cov-fail-under=90
UNIT_TEST_PATHS ?= tests/models
UNIT_COVERAGE_TARGET ?= app.models
UNIT_PYTEST_ARGS ?= -vv -ra --cov=$(UNIT_COVERAGE_TARGET) --cov-report=term-missing --cov-report=xml --cov-fail-under=70
INTEGRATION_TEST_PATHS ?= tests/repositories tests/routes tests/test_health.py tests/test_lifespan.py
RUFF ?= $(PYTHON) -m ruff
UV ?= uv
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

upgrade:
	uv pip compile $(REQ_IN) --generate-hashes --upgrade -o $(REQ_LOCK)
	uv pip install --python $(PYTHON) -r $(REQ_LOCK)

serve:
	$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

check:
	$(PYTEST) $(PYTEST_ARGS)

check-coverage:
	$(PYTEST) -vv -ra --cov=app --cov-report=term-missing --cov-report=xml --cov-fail-under=90

check-unit:
	$(PYTEST) $(UNIT_PYTEST_ARGS) $(UNIT_TEST_PATHS)

check-integration:
	$(PYTEST) -vv -ra $(INTEGRATION_TEST_PATHS)

lint:
	$(RUFF) check .

fix:
	$(RUFF) check . --fix

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache $(REQ_LOCK) coverage.xml

format:
	$(RUFF) format .

format-check:
	$(RUFF) format --check .

pre-commit:
	$(MAKE) format
	$(MAKE) lint
	@staged_files="$$(git diff --cached --name-only --diff-filter=ACMR)"; \
	[ -z "$$staged_files" ] || git diff --quiet -- $$staged_files || (echo "Formatting changed staged files. Stage changes and commit again." && exit 1)

audit:
	$(UV) run pip-audit

docker-run:
	docker compose up -d

docker-stop:
	docker compose down
