import json
from pathlib import Path

from eduslot.cli import main


def test_cli_solve_prints_schedule_result(tmp_path, capsys):
    workload_path = tmp_path / "workload.json"
    preferences_path = tmp_path / "preferences.json"

    _write_cli_input_files(workload_path, preferences_path)

    exit_code = main(
        [
            "solve",
            str(workload_path),
            str(preferences_path),
            "--max-time-seconds",
            "1",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"schedule"' in captured.out
    assert '"conflicts": []' in captured.out


def test_cli_variants_prints_variants(tmp_path, capsys):
    workload_path = tmp_path / "workload.json"
    preferences_path = tmp_path / "preferences.json"

    _write_cli_input_files(workload_path, preferences_path)

    exit_code = main(
        [
            "variants",
            str(workload_path),
            str(preferences_path),
            "--max-variants",
            "2",
            "--max-time-seconds",
            "1",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"variants"' in captured.out


def test_cli_metrics_prints_schedule_metrics(tmp_path, capsys):
    workload_path = tmp_path / "workload.json"
    preferences_path = tmp_path / "preferences.json"

    _write_cli_input_files(workload_path, preferences_path)

    exit_code = main(
        [
            "metrics",
            str(workload_path),
            str(preferences_path),
            "--max-time-seconds",
            "1",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert '"metrics"' in captured.out
    assert '"total_lessons": 1' in captured.out


def _write_cli_input_files(
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