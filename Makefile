.PHONY: default
default: help

.PHONY: help
help:
	@echo "make help              Show this help message"
	@echo "make dev               Run the app in the development server"
	@echo "make lint              Run the code linter(s) and print any warnings"
	@echo "make test              Run the unit tests"
	@echo "make docker            Make the app's Docker image"
	@echo "make clean             Delete development artefacts (cached files, "
	@echo "                       dependencies, etc)"

.PHONY: dev
dev:
	tox -e py27-dev

.PHONY: test
test:
	tox -e py27-tests

.PHONY: docker
docker:
	docker build -t hypothesis/via:$(DOCKER_TAG) .

.PHONY: lint
lint:
	tox -e py27-lint

.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

DOCKER_TAG = latest
