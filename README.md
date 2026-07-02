# EduSlot

EduSlot is an embeddable Python library for automatic educational timetable generation.

The library builds schedules from structured workload data, teacher preferences and scheduling constraints. EduSlot can be used inside an external educational service, from Python code, through CLI commands or through a demo Streamlit interface.

## Features

- Structured workload input for groups, subjects, teachers and weekly lesson counts.
- Teacher preference parsing from simple natural-language descriptions.
- Automatic timetable generation with OR-Tools CP-SAT.
- Conflict reporting for impossible scheduling cases.
- Schedule validation after generation.
- Input diagnostics before solver execution.
- Schedule metrics and group window counting.
- Alternative schedule variants.
- Export to JSON, CSV and XLSX.
- CLI, demo command and Streamlit demo interface.
- Sphinx documentation with Markdown pages and Mermaid diagrams.

## Project scope

EduSlot is not a full university management system.

It does not store users, groups, teachers or schedules in a database. It also does not provide authentication, user roles, schedule history or manual editing workflows.

EduSlot is designed as a scheduling engine. An external service can prepare input data, call the library and store or display the generated result.

## Installation

After publication, the package can be installed with pip:

```bash
pip install eduslot-scheduler
```

For local development, clone the repository and install dependencies:

```bash
git clone https://github.com/zenderio-dev/EduSlot.git
cd EduSlot
python -m pip install -r requirements.txt
```

## Quickstart

```python
from eduslot import generate_schedule, load_preferences, load_workload

workload = load_workload("data/sample_load.json")
preferences = load_preferences("data/sample_preferences.json")

result = generate_schedule(workload, preferences)

print(result.schedule)
print(result.warnings)
print(result.conflicts)
```

## Export

```python
from eduslot import (
    export_schedule_to_csv,
    export_schedule_to_json,
    export_schedule_to_xlsx,
    generate_schedule,
    load_preferences,
    load_workload,
)

workload = load_workload("data/sample_load.json")
preferences = load_preferences("data/sample_preferences.json")

result = generate_schedule(workload, preferences)

export_schedule_to_json(result, "outputs/schedule.json")
export_schedule_to_csv(result, "outputs/schedule.csv")
export_schedule_to_xlsx(result, "outputs/schedule.xlsx")
```

## CLI usage

Generate one schedule:

```bash
python -m eduslot.cli solve data/sample_load.json data/sample_preferences.json
```

Generate alternative variants:

```bash
python -m eduslot.cli variants data/sample_load.json data/sample_preferences.json --max-variants 3
```

Calculate metrics:

```bash
python -m eduslot.cli metrics data/sample_load.json data/sample_preferences.json
```

## Demo command

Run the sample demo:

```bash
python -m eduslot.demo
```

The command generates export files in the `outputs/` directory:

```text
outputs/schedule.json
outputs/schedule.csv
outputs/schedule.xlsx
```

## Streamlit demo

The project includes a visual demo interface:

```bash
streamlit run app.py
```

The Streamlit interface is a demonstration layer. It is useful for review, defense and visual project presentation, but it is not required for using EduSlot as a Python library.

## Documentation

Sphinx documentation is stored in `docs/source`.

Build documentation locally:

```bash
make docs
```

Open the generated HTML documentation:

```bash
docs/build/html/index.html
```

The documentation includes:

- installation guide;
- quickstart examples;
- architecture overview;
- Mermaid diagrams;
- input and output formats;
- API reference;
- examples;
- limitations.

## Development commands

Install dependencies:

```bash
make install
```

Run tests:

```bash
make test
```

Run checks:

```bash
make check
```

Run demo:

```bash
make demo
```

Run Streamlit interface:

```bash
make run
```

Build package:

```bash
make build
```

Check package distributions:

```bash
make package-check
```

## Input data

EduSlot expects structured workload JSON and teacher preferences JSON.

Workload example:

```json
{
  "groups": [
    {
      "name": "Group A",
      "lessons": [
        {
          "subject": "Python",
          "teacher": "Ivanov",
          "lessons_per_week": 2,
          "lesson_type": "practice"
        }
      ]
    }
  ]
}
```

Teacher preferences example:

```json
{
  "preferences": [
    {
      "teacher": "Ivanov",
      "text": "понедельник и среда"
    }
  ]
}
```

## Output

The main output type is `ScheduleResult`.

It contains:

- `schedule` — generated schedule items;
- `warnings` — non-critical warnings;
- `conflicts` — problems that prevented valid generation or validation.

## Limitations

Current limitations:

- fixed timetable grid;
- no classroom capacity support;
- no database storage;
- no user management;
- no schedule history;
- no manual schedule editing workflow;
- limited natural-language parsing for teacher preferences.

These features can be implemented in an external service or added as future EduSlot extensions.

## License

MIT License.
