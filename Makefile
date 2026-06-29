.PHONY: install test run demo lint clean

install:
	pip install -r requirements.txt

test:
	pytest

run:
	streamlit run app.py

demo:
	python -m eduslot.demo

lint:
	ruff check src tests

format:
	ruff format src tests

check:
	python -m compileall src
	ruff check src tests
	pytest

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"