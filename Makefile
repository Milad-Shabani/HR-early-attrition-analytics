.PHONY: install test build serve clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest -q

build:
	python -m attrition build

serve: build
	python -m http.server 8000 --directory docs

clean:
	rm -rf .pytest_cache build dist *.egg-info
