ENV_NAME=chess-env
ENV_FILE=environment.yml

.PHONY: env

env:
	@echo "Checking if Conda environment '$(ENV_NAME)' exists..."
	@if conda env list | grep -q '$(ENV_NAME)'; then \
		echo "Environment '$(ENV_NAME)' already exists."; \
	else \
		echo "Environment '$(ENV_NAME)' does not exist. Creating..."; \
		conda env create -f $(ENV_FILE); \
		echo "Environment '$(ENV_NAME)' created."; \
	fi
	@echo "To activate the environment, run: 'conda activate $(ENV_NAME)'"

.PHONY: test

test: env
	@echo "Running tests..."
	@PYTHONPATH=src conda run -n $(ENV_NAME) pytest