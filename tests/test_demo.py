import json
from pathlib import Path

from eduslot.demo import run_demo


def test_run_demo_generates_export_files(tmp_path):
    workload_path = tmp_path / "workload.json"
    preferences_path = tmp_path / "preferences.json"
    output_dir = tmp_path / "outputs"

    _write_demo_input_files(workload_path, preferences_path)

    result = run_demo(
        workload_path=workload_path,
        preferences_path=preferences_path,
        output_dir=output_dir,
    )

    assert result.conflicts == []
    assert len(result.schedule) == 1

    assert (output_dir / "schedule.json").exists()
    assert (output_dir / "schedule.csv").exists()
    assert (output_dir / "schedule.xlsx").exists()

    data = json.loads((output_dir / "schedule.json").read_text(encoding="utf-8"))

    assert data["schedule"][0]["group"] == "Group A"
    assert data["schedule"][0]["subject"] == "Python"


def _write_demo_input_files(
    workload_path: Path,
    preferences_path: Path,
) -> None:
    workload_path.write_text(
        json.dumps(
            {
                "groups": [
                    {
                        "name": "Group A",
                        "lessons": [
                            {
                                "subject": "Python",
                                "teacher": "Ivanov",
                                "lessons_per_week": 1,
                                "lesson_type": "practice",
                            }
                        ],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    preferences_path.write_text(
        json.dumps(
            {
                "preferences": [
                    {
                        "teacher": "Ivanov",
                        "text": "понедельник",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )