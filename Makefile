DOCKER_TAG = latest

.PHONY: docker
docker:
	docker build -t hypothesis/via:$(DOCKER_TAG) .

.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

.PHONY: deps
deps: requirements.txt requirements-dev.txt
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install pytest

.PHONY: test
test:
	python -m pytest tests

.PHONY: serve
serve:
	uwsgi uwsgi.ini

.PHONY: lint
lint:
	flake8 via tests
