import csv
import json
from pathlib import Path
from typing import TypeAlias

from openpyxl import Workbook

from eduslot.models import ScheduleItem, ScheduleResult


ScheduleExportInput: TypeAlias = ScheduleResult | list[ScheduleItem]

SCHEDULE_FIELDNAMES: list[str] = [
    "group",
    "subject",
    "teacher",
    "day",
    "slot",
    "lesson_type",
]


def export_schedule_to_json(
    schedule_data: ScheduleExportInput,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    _ensure_parent_directory(output_path)

    if isinstance(schedule_data, ScheduleResult):
        payload = schedule_data.model_dump(mode="json")
    else:
        payload = {
            "schedule": [
                item.model_dump(mode="json")
                for item in schedule_data
            ]
        }

    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return output_path


def export_schedule_to_csv(
    schedule_data: ScheduleExportInput,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    _ensure_parent_directory(output_path)

    schedule = _extract_schedule_items(schedule_data)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=SCHEDULE_FIELDNAMES)
        writer.writeheader()

        for item in schedule:
            writer.writerow(_schedule_item_to_row(item))

    return output_path


def export_schedule_to_xlsx(
    schedule_data: ScheduleExportInput,
    path: str | Path,
) -> Path:
    output_path = Path(path)
    _ensure_parent_directory(output_path)

    schedule = _extract_schedule_items(schedule_data)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Schedule"

    worksheet.append(SCHEDULE_FIELDNAMES)

    for item in schedule:
        row = _schedule_item_to_row(item)
        worksheet.append([row[field] for field in SCHEDULE_FIELDNAMES])

    workbook.save(output_path)

    return output_path


def _extract_schedule_items(schedule_data: ScheduleExportInput) -> list[ScheduleItem]:
    if isinstance(schedule_data, ScheduleResult):
        return schedule_data.schedule

    return schedule_data


def _schedule_item_to_row(item: ScheduleItem) -> dict[str, str | int]:
    return {
        "group": item.group,
        "subject": item.subject,
        "teacher": item.teacher,
        "day": item.day,
        "slot": item.slot,
        "lesson_type": item.lesson_type,
    }


def _ensure_parent_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)