# Architecture

EduSlot is organized as a small scheduling library with a clear separation between input loading, parsing, planning, solving, validation, metrics and export.

## High-level architecture

```{mermaid}
flowchart TD
    A["External service / CLI / Streamlit demo"] --> B["EduSlot public API"]
    B --> C["Input loading"]
    B --> D["Teacher preference parser"]
    B --> E["Planning"]
    E --> F["OR-Tools CP-SAT solver"]
    F --> G["ScheduleResult"]
    G --> H["Validators"]
    G --> I["Diagnostics"]
    G --> J["Metrics"]
    G --> K["Exporters"]
```

The external service is responsible for data storage, user management and business workflows. EduSlot receives structured data and returns a schedule result.

## Data flow

```{mermaid}
flowchart TD
    A["workload JSON"] --> C["load_workload"]
    B["preferences JSON"] --> D["load_preferences"]
    D --> E["parse_teacher_preference"]
    C --> F["build_lesson_units"]
    E --> G["generate_schedule"]
    F --> G
    G --> H["ScheduleResult"]
    H --> I["validate_schedule"]
    H --> J["summarize_schedule_metrics"]
    H --> K["export JSON / CSV / XLSX"]
```

The main data flow starts with JSON input files. EduSlot validates them with Pydantic models, converts teacher preference text into available timetable slots, expands weekly workload into lesson units and then runs the solver.

## Schedule generation sequence

```{mermaid}
sequenceDiagram
    participant User as User or external service
    participant API as EduSlot public API
    participant Parser as Preference parser
    participant Planner as Planning module
    participant Solver as OR-Tools solver
    participant Result as ScheduleResult

    User->>API: load workload and preferences
    API->>Parser: parse teacher preferences
    API->>Planner: build lesson units
    API->>Solver: generate schedule
    Solver->>Result: return schedule, warnings and conflicts
    Result->>User: provide generated result
```

## Main modules

| Module | Responsibility |
| --- | --- |
| `models.py` | Pydantic models for workload, preferences, schedule items and conflicts. |
| `io.py` | Loading and validation of JSON input files. |
| `parser.py` | Parsing text-based teacher preferences into available slots. |
| `planning.py` | Expanding weekly workload into individual lesson units. |
| `solver.py` | Automatic schedule generation with OR-Tools CP-SAT. |
| `validators.py` | Validation of generated schedules. |
| `diagnostics.py` | Pre-solver diagnostics for obvious input problems. |
| `metrics.py` | Schedule quality metrics and group window counting. |
| `exporter.py` | Export of generated schedules to JSON, CSV and XLSX. |
| `cli.py` | Command-line interface for solving, variants and metrics. |
| `demo.py` | Demonstration command based on sample input data. |
| `app.py` | Streamlit demo interface for visual project presentation. |

## Streamlit demo layer

The Streamlit interface is not the core of the library. It is a demonstration layer that uses the same public API as an external application would use.

```{mermaid}
flowchart LR
    A["Streamlit demo"] --> B["EduSlot public API"]
    C["CLI"] --> B
    D["External Python service"] --> B
    B --> E["Scheduling engine"]
```
