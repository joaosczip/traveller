start:
	poetry run uvicorn src.main:app --reload

test:
	poetry run pytest

lint:
	poetry run ruff check src
