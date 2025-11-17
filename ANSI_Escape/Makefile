.DEFAULT_GOAL := help
CURRENT_DIR := $(shell basename $(CURDIR))

build: ## Build the Docker image
	docker build --no-cache -t ansi_escape_app .

run: ## Run the Docker image
	docker run --rm -p 8080:8080 ansi_escape_app

remove: ## Remove the Docker image
	docker rmi ansi_escape_app

help:
	@echo "Make targets in $(CURRENT_DIR):"
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
