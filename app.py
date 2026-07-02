import json
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from pydantic import ValidationError

from eduslot import (
    PreferencesInput,
    ScheduleItem,
    ScheduleResult,
    WorkloadInput,
    generate_schedule,
    generate_schedule_variants,
    load_preferences,
    load_workload,
    summarize_schedule_metrics,
)
from eduslot.exporter import (
    export_schedule_to_csv,
    export_schedule_to_json,
    export_schedule_to_xlsx,
)


SAMPLE_WORKLOAD_PATH = Path("data/sample_load.json")
SAMPLE_PREFERENCES_PATH = Path("data/sample_preferences.json")


def main() -> None:
    st.set_page_config(
        page_title="EduSlot Demo",
        page_icon="📚",
        layout="wide",
    )

    st.title("EduSlot")
    st.caption("Automatic timetable generation module for educational schedules.")

    st.write(
        "This demo shows how EduSlot generates schedules from workload data, "
        "teacher preferences and scheduling constraints."
    )

    workload, preferences, max_time_seconds, max_variants = _render_sidebar()

    if workload is None or preferences is None:
        return

    if st.button("Generate schedule", type="primary"):
        with st.spinner("Generating schedule..."):
            result = generate_schedule(
                workload=workload,
                preferences=preferences,
                max_time_seconds=max_time_seconds,
            )
            variants = generate_schedule_variants(
                workload=workload,
                preferences=preferences,
                max_variants=max_variants,
                max_time_seconds=max_time_seconds,
            )

        st.session_state["schedule_result"] = result
        st.session_state["schedule_variants"] = variants

    result = st.session_state.get("schedule_result")
    variants = st.session_state.get("schedule_variants", [])

    if result is not None:
        _render_schedule_result(result)
        _render_schedule_variants(variants)
        _render_downloads(result)


def _render_sidebar() -> tuple[
    WorkloadInput | None,
    PreferencesInput | None,
    float,
    int,
]:
    st.sidebar.header("Input data")

    input_mode = st.sidebar.radio(
        "Data source",
        options=[
            "Use sample data",
            "Upload JSON files",
        ],
    )

    max_time_seconds = st.sidebar.number_input(
        "Max solver time, seconds",
        min_value=1.0,
        max_value=60.0,
        value=10.0,
        step=1.0,
    )

    max_variants = st.sidebar.number_input(
        "Max schedule variants",
        min_value=1,
        max_value=5,
        value=3,
        step=1,
    )

    if input_mode == "Use sample data":
        return (
            *_load_sample_inputs(),
            max_time_seconds,
            max_variants,
        )

    return (
        *_load_uploaded_inputs(),
        max_time_seconds,
        int(max_variants),
    )


def _load_sample_inputs() -> tuple[WorkloadInput | None, PreferencesInput | None]:
    st.sidebar.info(
        "Sample mode uses data/sample_load.json and "
        "data/sample_preferences.json."
    )

    try:
        workload = load_workload(SAMPLE_WORKLOAD_PATH)
        preferences = load_preferences(SAMPLE_PREFERENCES_PATH)
    except Exception as error:
        st.error(f"Failed to load sample data: {error}")
        return None, None

    return workload, preferences


def _load_uploaded_inputs() -> tuple[WorkloadInput | None, PreferencesInput | None]:
    workload_file = st.sidebar.file_uploader(
        "Upload workload JSON",
        type=["json"],
    )
    preferences_file = st.sidebar.file_uploader(
        "Upload preferences JSON",
        type=["json"],
    )

    if workload_file is None or preferences_file is None:
        st.info("Upload workload and preferences JSON files to continue.")
        return None, None

    try:
        workload_data = _read_uploaded_json(workload_file)
        preferences_data = _read_uploaded_json(preferences_file)

        workload = WorkloadInput.model_validate(workload_data)
        preferences = PreferencesInput.model_validate(preferences_data)
    except json.JSONDecodeError as error:
        st.error(f"Invalid JSON file: {error}")
        return None, None
    except ValidationError as error:
        st.error("Uploaded JSON does not match EduSlot input schema.")
        st.json(json.loads(error.json()))
        return None, None

    return workload, preferences


def _read_uploaded_json(uploaded_file: Any) -> dict[str, Any]:
    content = uploaded_file.getvalue().decode("utf-8")
    data = json.loads(content)

    if not isinstance(data, dict):
        raise ValueError("Uploaded JSON root must be an object.")

    return data


def _render_schedule_result(result: ScheduleResult) -> None:
    st.divider()
    st.header("Generated schedule")

    if result.conflicts:
        st.error("Schedule was not generated because conflicts were found.")
    else:
        st.success("Schedule generated successfully.")

    _render_warnings(result)
    _render_conflicts(result)

    if result.schedule:
        schedule_dataframe = _schedule_to_dataframe(result.schedule)
        st.dataframe(schedule_dataframe, use_container_width=True)
    else:
        st.info("No schedule items to display.")

    _render_metrics(result)


def _render_warnings(result: ScheduleResult) -> None:
    if not result.warnings:
        return

    with st.expander("Warnings", expanded=True):
        for warning in result.warnings:
            st.warning(warning)


def _render_conflicts(result: ScheduleResult) -> None:
    if not result.conflicts:
        return

    with st.expander("Conflicts", expanded=True):
        for conflict in result.conflicts:
            st.error(conflict.message)
            st.json(conflict.model_dump(mode="json"))


def _render_metrics(result: ScheduleResult) -> None:
    metrics = summarize_schedule_metrics(result.schedule)

    st.subheader("Schedule metrics")

    left_column, middle_column, right_column = st.columns(3)

    left_column.metric("Total lessons", metrics.total_lessons)
    middle_column.metric("Groups", len(metrics.lessons_per_group))
    right_column.metric("Teachers", len(metrics.lessons_per_teacher))

    with st.expander("Detailed metrics"):
        st.json(metrics.model_dump(mode="json"))


def _render_schedule_variants(variants: list[ScheduleResult]) -> None:
    if not variants:
        return

    st.divider()
    st.header("Alternative variants")

    for index, variant in enumerate(variants, start=1):
        with st.expander(f"Variant {index}"):
            if variant.conflicts:
                st.warning("This variant contains conflicts.")
                for conflict in variant.conflicts:
                    st.error(conflict.message)
                continue

            if variant.schedule:
                st.dataframe(
                    _schedule_to_dataframe(variant.schedule),
                    use_container_width=True,
                )
            else:
                st.info("No schedule items in this variant.")


def _render_downloads(result: ScheduleResult) -> None:
    st.divider()
    st.header("Export")

    json_bytes = _export_to_bytes(result, "json")
    csv_bytes = _export_to_bytes(result, "csv")
    xlsx_bytes = _export_to_bytes(result, "xlsx")

    left_column, middle_column, right_column = st.columns(3)

    left_column.download_button(
        label="Download JSON",
        data=json_bytes,
        file_name="schedule.json",
        mime="application/json",
    )

    middle_column.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name="schedule.csv",
        mime="text/csv",
    )

    right_column.download_button(
        label="Download XLSX",
        data=xlsx_bytes,
        file_name="schedule.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


def _export_to_bytes(result: ScheduleResult, file_format: str) -> bytes:
    with tempfile.TemporaryDirectory() as temporary_directory:
        output_path = Path(temporary_directory) / f"schedule.{file_format}"

        if file_format == "json":
            export_schedule_to_json(result, output_path)
        elif file_format == "csv":
            export_schedule_to_csv(result, output_path)
        elif file_format == "xlsx":
            export_schedule_to_xlsx(result, output_path)
        else:
            raise ValueError(f"Unsupported export format: {file_format}")

        return output_path.read_bytes()


def _schedule_to_dataframe(schedule: list[ScheduleItem]) -> pd.DataFrame:
    rows = [
        {
            "day": item.day,
            "slot": item.slot,
            "group": item.group,
            "subject": item.subject,
            "teacher": item.teacher,
            "lesson_type": item.lesson_type,
        }
        for item in schedule
    ]

    return pd.DataFrame(
        rows,
        columns=[
            "day",
            "slot",
            "group",
            "subject",
            "teacher",
            "lesson_type",
        ],
    )


if __name__ == "__main__":
    main()