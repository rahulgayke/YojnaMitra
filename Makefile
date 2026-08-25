.PHONY: install dev test test-unit test-integration lint format typecheck security up down logs clean

install:
	python -m pip install -e ".[dev]"

dev:
	uvicorn yojanamitra.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -q

test-unit:
	pytest tests/unit -q

test-integration:
	RUN_INTEGRATION=1 pytest tests/integration -q

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src

security:
	bandit -q -r src
	pip-audit

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build
