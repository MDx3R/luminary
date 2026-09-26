.DEFAULT_GOAL := help
.PHONY: help install reset check-lock test lint typecheck bandit xenon detect-secrets ci

POETRY ?= poetry

help:
	@echo "install         Poetry deps + pre-commit install"
	@echo "reset           docker compose down -v && up -d --build"
	@echo "check-lock      poetry check --lock"
	@echo "test            pytest (-q)"
	@echo "lint            ruff check (src, tests, cli)"
	@echo "typecheck       mypy (src, tests, cli)"
	@echo "bandit          bandit (-ll, pyproject config)"
	@echo "xenon           xenon (src, tests)"
	@echo "detect-secrets  detect-secrets-hook (.secrets.baseline)"
	@echo "ci              check-lock + steps from .github/workflows/ci.yml (no install, no gitleaks)"

install: check-lock
	$(POETRY) install --no-interaction --no-ansi
	$(POETRY) run pre-commit install

reset:
	docker compose down -v && docker compose up -d --build

check-lock:
	$(POETRY) check --lock

test:
	$(POETRY) run pytest -q

lint:
	$(POETRY) run ruff check src tests cli

typecheck:
	$(POETRY) run mypy src/ tests/ cli/

bandit:
	$(POETRY) run bandit -c pyproject.toml -r -ll src/ cli/

xenon:
	$(POETRY) run xenon src/ tests/ --max-absolute=B --max-modules=B --max-average=A

detect-secrets:
	$(POETRY) run detect-secrets-hook --baseline .secrets.baseline

ci: check-lock lint typecheck test
