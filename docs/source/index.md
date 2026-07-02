# EduSlot documentation

EduSlot is an embeddable Python library for automatic educational timetable generation.

The library builds schedules from structured workload data, teacher preferences and scheduling constraints. It can be used inside an external educational service, from Python code, through CLI commands or through a demo Streamlit interface.

## Main features

- Structured workload input for groups, subjects, teachers and weekly lesson counts.
- Teacher preference parsing from simple natural-language descriptions.
- Automatic schedule generation with OR-Tools CP-SAT.
- Conflict reporting for impossible scheduling cases.
- Schedule validation after generation.
- Input diagnostics before solver execution.
- Schedule metrics and group window counting.
- Alternative schedule variants.
- Export to JSON, CSV and XLSX.
- CLI, demo command and visual Streamlit demonstration.

## Project scope

EduSlot is not a complete university management system. It does not store users, teachers, groups or schedules in a database.

The library expects input data from an external system and returns a generated schedule result. A web service, desktop application or educational platform can use EduSlot as a scheduling engine.

```{toctree}
:maxdepth: 2
:caption: Contents

installation
quickstart
architecture
input_output
api
examples
limitations
```
