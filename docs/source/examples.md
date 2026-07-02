# Examples

This page contains practical EduSlot usage examples.

## Generate a schedule

```python
from eduslot import generate_schedule, load_preferences, load_workload

workload = load_workload("data/sample_load.json")
preferences = load_preferences("data/sample_preferences.json")

result = generate_schedule(workload, preferences)

if result.conflicts:
    for conflict in result.conflicts:
        print(conflict.message)
else:
    for item in result.schedule:
        print(item)
```

## Export a schedule

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

## Generate alternative variants

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
    print(f"Variant {index}: {len(variant.schedule)} lessons")
```

## Run diagnostics before solving

```python
from eduslot import diagnose_schedule_inputs, load_preferences, load_workload

workload = load_workload("data/sample_load.json")
preferences = load_preferences("data/sample_preferences.json")

conflicts = diagnose_schedule_inputs(workload, preferences)

for conflict in conflicts:
    print(conflict.message)
```

## Validate a generated schedule

```python
from eduslot import (
    generate_schedule,
    load_preferences,
    load_workload,
    validate_schedule,
)

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

print(metrics.total_lessons)
print(metrics.lessons_per_group)
print(metrics.group_windows)
```

## CLI examples

Generate a schedule:

```bash
python -m eduslot.cli solve data/sample_load.json data/sample_preferences.json
```

Generate variants:

```bash
python -m eduslot.cli variants data/sample_load.json data/sample_preferences.json --max-variants 3
```

Print metrics:

```bash
python -m eduslot.cli metrics data/sample_load.json data/sample_preferences.json
```

Run the demo:

```bash
python -m eduslot.demo
```
