from pathlib import Path

from eduslot import (
    export_schedule_to_csv,
    export_schedule_to_json,
    export_schedule_to_xlsx,
    generate_schedule,
    load_preferences,
    load_workload,
)
from eduslot.models import ScheduleResult


DEFAULT_WORKLOAD_PATH = Path("data/sample_load.json")
DEFAULT_PREFERENCES_PATH = Path("data/sample_preferences.json")
DEFAULT_OUTPUT_DIR = Path("outputs")


def run_demo(
    workload_path: str | Path = DEFAULT_WORKLOAD_PATH,
    preferences_path: str | Path = DEFAULT_PREFERENCES_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
) -> ScheduleResult:
    workload = load_workload(workload_path)
    preferences = load_preferences(preferences_path)

    result = generate_schedule(workload, preferences)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    export_schedule_to_json(result, output_path / "schedule.json")
    export_schedule_to_csv(result, output_path / "schedule.csv")
    export_schedule_to_xlsx(result, output_path / "schedule.xlsx")

    return result


def main() -> int:
    result = run_demo()

    print("EduSlot demo completed.")
    print(f"Lessons: {len(result.schedule)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Conflicts: {len(result.conflicts)}")
    print()
    print("Exported files:")
    print("outputs/schedule.json")
    print("outputs/schedule.csv")
    print("outputs/schedule.xlsx")

    if result.warnings:
        print()
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")

    if result.conflicts:
        print()
        print("Conflicts:")
        for conflict in result.conflicts:
            print(f"- {conflict.message}")

    return 0 if not result.conflicts else 1


if __name__ == "__main__":
    raise SystemExit(main())