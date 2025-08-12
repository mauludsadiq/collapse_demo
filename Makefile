# Makefile
PY ?= python
PIP ?= pip

SCENARIOS := basic coref tense kb

.PHONY: help
help:
	@echo "Targets:"
	@echo "  setup       - install deps from requirements.txt"
	@echo "  test        - run pytest"
	@echo "  run-all     - run all scenarios with --json --verify"
	@echo "  clean       - remove artifacts and caches"

.PHONY: setup
setup:
	$(PIP) install -r requirements.txt

.PHONY: test
test:
	pytest -q

.PHONY: run-all
run-all:
	@for s in $(SCENARIOS); do \
		echo "=== Running $$s ==="; \
		$(PY) demo_runner.py --scenario $$s --json --verify --print || exit 1; \
		echo; \
	done

.PHONY: clean
clean:
	rm -rf artifacts .pytest_cache __pycache__
