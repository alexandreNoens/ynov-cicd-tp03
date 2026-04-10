.PHONY: help install install-hooks install-db upgrade check check-unit check-integration format format-check lint fix pre-commit audit serve docker-run docker-stop clean

# --- Tooling and runtime ---
VENV ?= .venv
PYTHON ?= $(VENV)/bin/python
UV ?= uv
UVICORN ?= $(PYTHON) -m uvicorn
PYTEST ?= $(PYTHON) -m pytest
RUFF ?= $(PYTHON) -m ruff

# --- Project settings ---
APP ?= app.main:app
HOST ?= 0.0.0.0
PORT ?= 8000
REQ_DIR ?= requirements
REQ_IN ?= $(REQ_DIR)/requirements.in
REQ_LOCK ?= $(REQ_DIR)/requirements.lock

# --- Test settings ---
PYTEST_COMMON_ARGS ?= -vv -ra
PYTEST_COVERAGE_REPORT_ARGS ?= --cov-report=term-missing
PYTEST_COV_FAIL_UNDER ?= 90
PYTEST_COV_FAIL_UNDER_ARG ?= --cov-fail-under=$(PYTEST_COV_FAIL_UNDER)

PYTEST_ARGS ?= $(PYTEST_COMMON_ARGS) --cov=app $(PYTEST_COVERAGE_REPORT_ARGS) $(PYTEST_COV_FAIL_UNDER_ARG)
UNIT_TEST_PATHS ?= tests/models
UNIT_COVERAGE_TARGET ?= app.models
UNIT_PYTEST_ARGS ?= $(PYTEST_COMMON_ARGS) --cov=$(UNIT_COVERAGE_TARGET) $(PYTEST_COVERAGE_REPORT_ARGS) $(PYTEST_COV_FAIL_UNDER_ARG)
INTEGRATION_TEST_PATHS ?= tests/repositories tests/routes tests/test_health.py tests/test_lifespan.py
INTEGRATION_COVERAGE_TARGET ?= app
INTEGRATION_PYTEST_ARGS ?= $(PYTEST_COMMON_ARGS) --cov=$(INTEGRATION_COVERAGE_TARGET) $(PYTEST_COVERAGE_REPORT_ARGS) $(PYTEST_COV_FAIL_UNDER_ARG)

# --- Environment setup ---
help:
	@printf "Available commands:\n\n"
	@printf "Environment setup:\n"
	@printf "  make install            Create the virtual environment and install locked dependencies\n"
	@printf "  make install-hooks      Configure git hooks for the repository\n"
	@printf "  make install-db         Reset and initialize the local database\n"
	@printf "  make upgrade            Refresh the lockfile and upgrade dependencies\n\n"
	@printf "Tests:\n"
	@printf "  make check              Run the full test suite with coverage\n"
	@printf "  make check-unit         Run unit tests with coverage\n"
	@printf "  make check-integration  Run integration tests with coverage\n\n"
	@printf "Code quality:\n"
	@printf "  make format             Format the codebase with Ruff\n"
	@printf "  make format-check       Verify formatting without changing files\n"
	@printf "  make lint               Run static checks with Ruff\n"
	@printf "  make fix                Apply automatic Ruff fixes\n"
	@printf "  make pre-commit         Run formatting and lint checks used by the git hook\n"
	@printf "  make audit              Scan Python dependencies for known vulnerabilities\n\n"
	@printf "App and containers:\n"
	@printf "  make serve              Start the API locally with auto-reload\n"
	@printf "  make docker-run         Start services with docker compose\n"
	@printf "  make docker-stop        Stop docker compose services\n\n"
	@printf "Cleanup:\n"
	@printf "  make clean              Remove caches, the virtual environment, and the lockfile\n"

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

# --- Test commands ---
check:
	$(PYTEST) $(PYTEST_ARGS)

check-unit:
	$(PYTEST) $(UNIT_PYTEST_ARGS) $(UNIT_TEST_PATHS)

check-integration:
	$(PYTEST) $(INTEGRATION_PYTEST_ARGS) $(INTEGRATION_TEST_PATHS)

# --- Code quality ---
format:
	$(RUFF) format .

format-check:
	$(RUFF) format --check .

lint:
	$(RUFF) check .

fix:
	$(RUFF) check . --fix

pre-commit:
	$(MAKE) format
	$(MAKE) lint
	@staged_files="$$(git diff --cached --name-only --diff-filter=ACMR)"; \
	[ -z "$$staged_files" ] || git diff --quiet -- $$staged_files || (echo "Formatting changed staged files. Stage changes and commit again." && exit 1)

audit:
	$(UV) run pip-audit

# --- App and containers ---
serve:
	$(UVICORN) $(APP) --reload --host $(HOST) --port $(PORT)

docker-run:
	docker compose up -d

docker-stop:
	docker compose down

# --- Cleanup ---
clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache $(REQ_LOCK)
