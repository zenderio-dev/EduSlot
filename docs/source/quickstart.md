# Quickstart

This page shows the basic EduSlot workflow.

## Python API usage

Load input data, generate a schedule and inspect the result:

```python
from eduslot import generate_schedule, load_preferences, load_workload

workload = load_workload("data/sample_load.json")
preferences = load_preferences("data/sample_preferences.json")

result = generate_schedule(workload, preferences)

print(result.schedule)
print(result.warnings)
print(result.conflicts)
```

## Export generated schedule

EduSlot can export generated schedules to JSON, CSV and XLSX:

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

## Generate schedule variants

```python
from eduslot import generate_schedule_variants, load_preferences, load_workload

workload = load_workload("data/sample_load.json")
preferences = load_preferences("data/sample_preferences.json")

variants = generate_schedule_variants(
    workload=workload,
    preferences=preferences,
    max_variants=3,
)

for index, variant in enumerate(variants, start=1):
    print(f"Variant {index}")
    print(variant.schedule)
```

## Validate generated schedule

```python
from eduslot import generate_schedule, load_preferences, load_workload, validate_schedule

workload = load_workload("data/sample_load.json")
preferences = load_preferences("data/sample_preferences.json")

result = generate_schedule(workload, preferences)
conflicts = validate_schedule(result.schedule, workload, preferences)

print(conflicts)
```

## Calculate metrics

```python
from eduslot import generate_schedule, load_preferences, load_workload, summarize_schedule_metrics

workload = load_workload("data/sample_load.json")
preferences = load_preferences("data/sample_preferences.json")

result = generate_schedule(workload, preferences)
metrics = summarize_schedule_metrics(result.schedule)

print(metrics.model_dump())
```
