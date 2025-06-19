start:
	poetry run uvicorn src.main:app --reload

test:
	PYTHONPATH=. poetry run pytest -v

test-coverage:
	PYTHONPATH=. poetry run pytest --cov=src --cov-report=html --cov-report=term-missing -v

test-watch:
	PYTHONPATH=. poetry run pytest-watch -- -v

lint:
	poetry run ruff check src

start-redis:
	docker compose up -d redis

.PHONY: start test test-coverage test-watch lint start-redis
