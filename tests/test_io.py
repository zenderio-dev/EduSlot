import json

import pytest

from eduslot.io import InputDataError, load_json_file, load_preferences, load_workload
from eduslot.models import PreferencesInput, WorkloadInput


def test_load_json_file_returns_dictionary(tmp_path):
    input_file = tmp_path / "input.json"
    input_file.write_text('{"name": "EduSlot"}', encoding="utf-8")

    data = load_json_file(input_file)

    assert data == {"name": "EduSlot"}


def test_load_json_file_rejects_missing_file(tmp_path):
    missing_file = tmp_path / "missing.json"

    with pytest.raises(InputDataError):
        load_json_file(missing_file)


def test_load_json_file_rejects_invalid_json(tmp_path):
    input_file = tmp_path / "broken.json"
    input_file.write_text("{broken json", encoding="utf-8")

    with pytest.raises(InputDataError):
        load_json_file(input_file)


def test_load_json_file_rejects_non_object_json(tmp_path):
    input_file = tmp_path / "list.json"
    input_file.write_text('["not", "object"]', encoding="utf-8")

    with pytest.raises(InputDataError):
        load_json_file(input_file)


def test_load_workload_from_sample_file():
    workload = load_workload("data/sample_load.json")

    assert isinstance(workload, WorkloadInput)
    assert len(workload.groups) > 0
    assert len(workload.groups[0].lessons) > 0


def test_load_preferences_from_sample_file():
    preferences = load_preferences("data/sample_preferences.json")

    assert isinstance(preferences, PreferencesInput)
    assert len(preferences.preferences) > 0


def test_load_workload_rejects_invalid_structure(tmp_path):
    input_file = tmp_path / "invalid_workload.json"
    input_file.write_text(
        json.dumps({"groups": []}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(InputDataError):
        load_workload(input_file)


def test_load_preferences_rejects_invalid_structure(tmp_path):
    input_file = tmp_path / "invalid_preferences.json"
    input_file.write_text(
        json.dumps({"preferences": [{"teacher": "", "text": ""}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    with pytest.raises(InputDataError):
        load_preferences(input_file)