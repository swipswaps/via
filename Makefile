DOCKER_TAG = latest

.PHONY: docker
docker:
	docker build -t hypothesis/via:$(DOCKER_TAG) .

.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

.pydeps: requirements.txt requirements-dev.txt
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install pytest
	touch $@

.PHONY: test
test: .pydeps
	python -m pytest tests

.PHONY: serve
serve: .pydeps
	uwsgi uwsgi.ini

.PHONY: lint
lint: .pydeps
	flake8 via tests
