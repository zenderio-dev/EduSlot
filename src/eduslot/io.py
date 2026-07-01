import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from eduslot.models import PreferencesInput, WorkloadInput


class InputDataError(ValueError):
    """Raised when an input file cannot be loaded or validated."""


def load_json_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)

    try:
        content = file_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise InputDataError(f"Input file not found: {file_path}") from error

    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        raise InputDataError(f"Invalid JSON file: {file_path}") from error

    if not isinstance(data, dict):
        raise InputDataError(f"Input JSON root must be an object: {file_path}")

    return data


def load_workload(path: str | Path) -> WorkloadInput:
    data = load_json_file(path)

    try:
        return WorkloadInput.model_validate(data)
    except ValidationError as error:
        raise InputDataError(f"Invalid workload input: {path}") from error


def load_preferences(path: str | Path) -> PreferencesInput:
    data = load_json_file(path)

    try:
        return PreferencesInput.model_validate(data)
    except ValidationError as error:
        raise InputDataError(f"Invalid preferences input: {path}") from error