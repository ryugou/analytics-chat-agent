.PHONY: format lint test clean lint-fix

format:
	poetry run black .
	poetry run isort .
	poetry run ruff check --fix src tests

lint:
	poetry run flake8 src tests
	poetry run mypy src tests
	poetry run black . --check
	poetry run isort . --check-only

test:
	PYTHONPATH=src poetry run pytest

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +
	find . -type d -name "build" -exec rm -r {} +

lint-fix:
	poetry run black .
	poetry run isort . 