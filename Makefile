.PHONY: install test run demo cli-solve cli-variants cli-metrics docs docs-clean build package-check lint format check clean

PYTHON ?= python
PYTHONPATH ?= src

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest

run:
	PYTHONPATH=$(PYTHONPATH) streamlit run app.py

demo:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m eduslot.demo

cli-solve:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m eduslot.cli solve data/sample_load.json data/sample_preferences.json

cli-variants:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m eduslot.cli variants data/sample_load.json data/sample_preferences.json --max-variants 3

cli-metrics:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m eduslot.cli metrics data/sample_load.json data/sample_preferences.json

docs:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m sphinx -b html docs/source docs/build/html

docs-clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('docs/build', ignore_errors=True)"

build:
	$(PYTHON) -m build

package-check:
	$(PYTHON) -m twine check dist/*

lint:
	$(PYTHON) -m ruff check src tests

format:
	$(PYTHON) -m ruff format src tests

check:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m compileall src
	$(PYTHON) -m ruff check src tests
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import shutil; shutil.rmtree('dist', ignore_errors=True); shutil.rmtree('build', ignore_errors=True); shutil.rmtree('docs/build', ignore_errors=True)"