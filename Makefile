# ============================================================================
#  Makefile - A_maze_ing application
# ============================================================================

NAME       := a_maze_ing.py
PACKAGE    := mazegen
CONFIG     ?= config.txt

VENV       := venv
LOCAL_PY   := python3
PIP        := $(VENV)/bin/pip
PY         := $(VENV)/bin/python
FLAKE8     := $(VENV)/bin/flake8
MYPY       := $(VENV)/bin/mypy

# Files that trigger a new installation of the dependencies when they change
DEPS       := $(wildcard requirements.txt pyproject.toml setup.py)
STAMP      := $(VENV)/.installed

# Folders ignored by the linters
FLAKE8_EXCLUDE := $(VENV),build,dist,.mypy_cache
MYPY_EXCLUDE   := ^($(VENV)|build|dist)/

MYPY_FLAGS := --warn-return-any --warn-unused-ignores --ignore-missing-imports \
              --disallow-untyped-defs --check-untyped-defs

.PHONY: all venv install run debug package lint lint-strict clean fclean re

all: install

# --- Virtual environment ----------------------------------------------------
venv: $(VENV)/bin/activate

$(VENV)/bin/activate:
	$(LOCAL_PY) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy build
	@echo "Virtual environment created successfully!"

# --- Project dependencies ---------------------------------------------------
install: $(STAMP)

$(STAMP): $(VENV)/bin/activate $(DEPS)
	@if [ -f requirements.txt ]; then $(PIP) install -r requirements.txt; fi
	@if [ -f pyproject.toml ] || [ -f setup.py ]; then $(PIP) install -e .; fi
	@touch $(STAMP)
	@echo "Dependencies installed!"

# --- Execution --------------------------------------------------------------
# Usage: make run (uses config.txt)
# make run CONFIG=other.txt
run: install
	$(PY) $(NAME) $(CONFIG)

debug: install
	$(PY) -m pdb $(NAME) $(CONFIG)

# --- Package (.whl) ---------------------------------------------------------
package: install
	$(PY) -m build
	cp dist/$(PACKAGE)-*.whl .
	@echo "Package built: $(PACKAGE)-*.whl"

# --- Code quality -----------------------------------------------------------
lint: install
	$(FLAKE8) . --extend-exclude $(FLAKE8_EXCLUDE)
	$(MYPY) . $(MYPY_FLAGS) --exclude '$(MYPY_EXCLUDE)'

lint-strict: install
	$(FLAKE8) . --extend-exclude $(FLAKE8_EXCLUDE)
	$(MYPY) . --strict --ignore-missing-imports --exclude '$(MYPY_EXCLUDE)'

# --- Cleanup ----------------------------------------------------------------
# clean : removes only caches (keeps the venv)
clean:
	find . -type d \( -name __pycache__ -o -name .mypy_cache \) \
		-not -path "./$(VENV)/*" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -not -path "./$(VENV)/*" -delete
	rm -rf .mypy_cache
	@echo "Cache removed!"

# fclean: removes everything the Makefile produced
fclean: clean
	rm -rf $(VENV) build dist *.egg-info *.whl
	@echo "Virtual environment and build artifacts removed!"

re: fclean all
