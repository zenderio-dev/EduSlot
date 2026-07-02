# Installation

EduSlot is designed as an installable Python library.

## Requirements

Recommended environment:

- Python 3.10+
- pip
- virtual environment

## Local development installation

Clone the project and install dependencies:

```bash
git clone https://github.com/<your-username>/EduSlot.git
cd EduSlot
python -m pip install -r requirements.txt
```

Run tests:

```bash
pytest
```

Or use the project Makefile:

```bash
make test
```

## Running the demo locally

EduSlot includes a demo command based on sample input files:

```bash
make demo
```

The command generates schedule export files in the `outputs/` directory:

```text
outputs/schedule.json
outputs/schedule.csv
outputs/schedule.xlsx
```

## Running the CLI locally

Generate a schedule from JSON files:

```bash
python -m eduslot.cli solve data/sample_load.json data/sample_preferences.json
```

Generate alternative schedule variants:

```bash
python -m eduslot.cli variants data/sample_load.json data/sample_preferences.json --max-variants 3
```

Calculate schedule metrics:

```bash
python -m eduslot.cli metrics data/sample_load.json data/sample_preferences.json
```

## Streamlit demo

The project also includes a visual demo interface:

```bash
make run
```

The Streamlit interface is a demonstration layer. It is not required for using EduSlot as a library.
