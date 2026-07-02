from eduslot.diagnostics import (
    diagnose_group_capacity,
    diagnose_schedule_inputs,
    diagnose_teacher_availability,
)
from eduslot.exporter import (
    export_schedule_to_csv,
    export_schedule_to_json,
    export_schedule_to_xlsx,
)
from eduslot.io import load_preferences, load_workload
from eduslot.metrics import (
    count_group_windows,
    count_group_windows_by_day,
    count_lessons_per_group,
    count_lessons_per_teacher,
    summarize_schedule_metrics,
)
from eduslot.models import (
    Conflict,
    GroupLoad,
    LessonLoad,
    PreferencesInput,
    ScheduleItem,
    ScheduleResult,
    TeacherAvailability,
    TeacherPreferenceInput,
    TimeSlot,
    WorkloadInput,
)
from eduslot.parser import parse_preference_input, parse_teacher_preference
from eduslot.planning import LessonUnit, build_lesson_units, count_total_lessons
from eduslot.solver import generate_schedule, generate_schedule_variants
from eduslot.validators import (
    validate_group_overlaps,
    validate_required_load,
    validate_schedule,
    validate_teacher_availability,
    validate_teacher_overlaps,
)


__version__ = "0.1.0"


__all__ = [
    "__version__",
    "Conflict",
    "GroupLoad",
    "LessonLoad",
    "LessonUnit",
    "PreferencesInput",
    "ScheduleItem",
    "ScheduleResult",
    "TeacherAvailability",
    "TeacherPreferenceInput",
    "TimeSlot",
    "WorkloadInput",
    "build_lesson_units",
    "count_group_windows",
    "count_group_windows_by_day",
    "count_lessons_per_group",
    "count_lessons_per_teacher",
    "count_total_lessons",
    "diagnose_group_capacity",
    "diagnose_schedule_inputs",
    "diagnose_teacher_availability",
    "export_schedule_to_csv",
    "export_schedule_to_json",
    "export_schedule_to_xlsx",
    "generate_schedule",
    "generate_schedule_variants",
    "load_preferences",
    "load_workload",
    "parse_preference_input",
    "parse_teacher_preference",
    "summarize_schedule_metrics",
    "validate_group_overlaps",
    "validate_required_load",
    "validate_schedule",
    "validate_teacher_availability",
    "validate_teacher_overlaps",
]