from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from ortools.sat.python import cp_model

from eduslot.models import (
    Conflict,
    Day,
    PreferencesInput,
    ScheduleItem,
    ScheduleResult,
    TimeSlot,
    WorkloadInput,
)
from eduslot.parser import parse_preference_input
from eduslot.planning import LessonUnit, build_lesson_units
from eduslot.time_grid import get_all_slots


SlotKey = tuple[Day, int]
AssignmentSignature = frozenset[tuple[int, SlotKey]]
VisibleScheduleSignature = frozenset[tuple[str, str, str, Day, int, str]]

DAY_ORDER: list[Day] = ["mon", "tue", "wed", "thu", "fri"]


@dataclass(frozen=True)
class SolverOutcome:
    """Internal result of one solver run."""
    result: ScheduleResult
    assignment_signature: AssignmentSignature | None = None


def generate_schedule(
    workload: WorkloadInput,
    preferences: PreferencesInput,
    max_time_seconds: float = 10.0,
) -> ScheduleResult:
    """Generate one schedule from workload and teacher preferences."""
    outcome = _solve_schedule(
        workload=workload,
        preferences=preferences,
        max_time_seconds=max_time_seconds,
        forbidden_schedules=[],
    )

    return outcome.result


def generate_schedule_variants(
    workload: WorkloadInput,
    preferences: PreferencesInput,
    max_variants: int = 3,
    max_time_seconds: float = 10.0,
) -> list[ScheduleResult]:
    """Generate several alternative schedule variants."""
    if max_variants <= 0:
        return []

    variants: list[ScheduleResult] = []
    forbidden_schedules: list[AssignmentSignature] = []
    seen_visible_schedules: set[VisibleScheduleSignature] = set()

    max_attempts = max_variants * 5

    for _ in range(max_attempts):
        if len(variants) >= max_variants:
            break

        outcome = _solve_schedule(
            workload=workload,
            preferences=preferences,
            max_time_seconds=max_time_seconds,
            forbidden_schedules=forbidden_schedules,
        )

        if outcome.result.conflicts:
            if not variants:
                variants.append(outcome.result)
            break

        if outcome.assignment_signature is None:
            break

        forbidden_schedules.append(outcome.assignment_signature)

        visible_signature = _build_visible_schedule_signature(outcome.result.schedule)

        if visible_signature in seen_visible_schedules:
            continue

        seen_visible_schedules.add(visible_signature)
        variants.append(outcome.result)

    return variants


def _solve_schedule(
    workload: WorkloadInput,
    preferences: PreferencesInput,
    max_time_seconds: float,
    forbidden_schedules: list[AssignmentSignature],
) -> SolverOutcome:
    lesson_units = build_lesson_units(workload)
    all_slots = get_all_slots()

    availability_by_teacher, warnings = _build_availability_by_teacher(
        preferences=preferences,
    )

    for lesson_unit in lesson_units:
        availability_by_teacher.setdefault(
            lesson_unit.teacher,
            _to_slot_keys(all_slots),
        )

    no_slot_conflict = _find_lesson_without_available_slots(
        lesson_units=lesson_units,
        availability_by_teacher=availability_by_teacher,
    )
    if no_slot_conflict is not None:
        return SolverOutcome(
            result=ScheduleResult(
                schedule=[],
                warnings=warnings,
                conflicts=[no_slot_conflict],
            )
        )

    model = cp_model.CpModel()

    assignment_vars: dict[tuple[int, SlotKey], cp_model.IntVar] = {}
    lesson_vars: dict[int, list[cp_model.IntVar]] = defaultdict(list)

    teacher_slot_vars: dict[tuple[str, SlotKey], list[cp_model.IntVar]] = defaultdict(
        list
    )
    group_slot_vars: dict[tuple[str, SlotKey], list[cp_model.IntVar]] = defaultdict(
        list
    )

    for lesson_index, lesson_unit in enumerate(lesson_units):
        available_slots = availability_by_teacher[lesson_unit.teacher]

        for slot_key in sorted(available_slots, key=_slot_sort_key):
            variable = model.NewBoolVar(
                f"lesson_{lesson_index}_at_{slot_key[0]}_{slot_key[1]}"
            )

            assignment_vars[(lesson_index, slot_key)] = variable
            lesson_vars[lesson_index].append(variable)
            teacher_slot_vars[(lesson_unit.teacher, slot_key)].append(variable)
            group_slot_vars[(lesson_unit.group, slot_key)].append(variable)

    for variables in lesson_vars.values():
        model.AddExactlyOne(variables)

    for variables in teacher_slot_vars.values():
        model.AddAtMostOne(variables)

    for variables in group_slot_vars.values():
        model.AddAtMostOne(variables)

    _add_forbidden_schedule_constraints(
        model=model,
        assignment_vars=assignment_vars,
        forbidden_schedules=forbidden_schedules,
    )

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_time_seconds

    status = solver.Solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return SolverOutcome(
            result=ScheduleResult(
                schedule=[],
                warnings=warnings,
                conflicts=[
                    Conflict(
                        type="no_valid_schedule",
                        message=(
                            "Не удалось построить расписание при заданной нагрузке, "
                            "доступности преподавателей и жестких ограничениях."
                        ),
                        affected_groups=_unique(unit.group for unit in lesson_units),
                        affected_teachers=_unique(
                            unit.teacher for unit in lesson_units
                        ),
                    )
                ],
            )
        )

    schedule = _build_schedule_from_solution(
        solver=solver,
        assignment_vars=assignment_vars,
        lesson_units=lesson_units,
    )
    assignment_signature = _build_assignment_signature(
        solver=solver,
        assignment_vars=assignment_vars,
    )

    return SolverOutcome(
        result=ScheduleResult(
            schedule=schedule,
            warnings=warnings,
            conflicts=[],
        ),
        assignment_signature=assignment_signature,
    )


def _add_forbidden_schedule_constraints(
    model: cp_model.CpModel,
    assignment_vars: dict[tuple[int, SlotKey], cp_model.IntVar],
    forbidden_schedules: list[AssignmentSignature],
) -> None:
    for forbidden_schedule in forbidden_schedules:
        matching_variables = [
            assignment_vars[(lesson_index, slot_key)]
            for lesson_index, slot_key in forbidden_schedule
            if (lesson_index, slot_key) in assignment_vars
        ]

        if not matching_variables:
            continue

        model.Add(sum(matching_variables) <= len(matching_variables) - 1)


def _build_availability_by_teacher(
    preferences: PreferencesInput,
) -> tuple[dict[str, set[SlotKey]], list[str]]:
    availability_by_teacher: dict[str, set[SlotKey]] = {}
    warnings: list[str] = []

    for preference in preferences.preferences:
        availability = parse_preference_input(preference)

        if availability.warnings:
            warnings.extend(
                _format_availability_warnings(
                    teacher=availability.teacher,
                    warnings=availability.warnings,
                )
            )

        availability_by_teacher.setdefault(availability.teacher, set())
        availability_by_teacher[availability.teacher].update(
            _to_slot_keys(availability.available_slots)
        )

    if not preferences.preferences:
        warnings.append(
            "Пожелания преподавателей не заданы. "
            "Для всех преподавателей используется полная сетка расписания."
        )

    return availability_by_teacher, warnings


def _find_lesson_without_available_slots(
    lesson_units: list[LessonUnit],
    availability_by_teacher: dict[str, set[SlotKey]],
) -> Conflict | None:
    for lesson_unit in lesson_units:
        available_slots = availability_by_teacher.get(lesson_unit.teacher, set())

        if not available_slots:
            return Conflict(
                type="teacher_availability",
                message=(
                    f"Для преподавателя {lesson_unit.teacher} нет доступных слотов "
                    f"для занятия {lesson_unit.subject} у группы {lesson_unit.group}."
                ),
                affected_groups=[lesson_unit.group],
                affected_teachers=[lesson_unit.teacher],
            )

    return None


def _build_schedule_from_solution(
    solver: cp_model.CpSolver,
    assignment_vars: dict[tuple[int, SlotKey], cp_model.IntVar],
    lesson_units: list[LessonUnit],
) -> list[ScheduleItem]:
    schedule: list[ScheduleItem] = []

    for (lesson_index, slot_key), variable in assignment_vars.items():
        if solver.BooleanValue(variable):
            lesson_unit = lesson_units[lesson_index]
            day, slot = slot_key

            schedule.append(
                ScheduleItem(
                    group=lesson_unit.group,
                    subject=lesson_unit.subject,
                    teacher=lesson_unit.teacher,
                    day=day,
                    slot=slot,
                    lesson_type=lesson_unit.lesson_type,
                )
            )

    return sorted(schedule, key=_schedule_sort_key)


def _build_assignment_signature(
    solver: cp_model.CpSolver,
    assignment_vars: dict[tuple[int, SlotKey], cp_model.IntVar],
) -> AssignmentSignature:
    assignments: set[tuple[int, SlotKey]] = set()

    for assignment_key, variable in assignment_vars.items():
        if solver.BooleanValue(variable):
            assignments.add(assignment_key)

    return frozenset(assignments)


def _build_visible_schedule_signature(
    schedule: list[ScheduleItem],
) -> VisibleScheduleSignature:
    return frozenset(
        (
            item.group,
            item.subject,
            item.teacher,
            item.day,
            item.slot,
            item.lesson_type,
        )
        for item in schedule
    )


def _format_availability_warnings(teacher: str, warnings: list[str]) -> list[str]:
    return [f"{teacher}: {warning}" for warning in warnings]


def _to_slot_keys(slots: Iterable[TimeSlot]) -> set[SlotKey]:
    return {(slot.day, slot.slot) for slot in slots}


def _slot_sort_key(slot_key: SlotKey) -> tuple[int, int]:
    day, slot = slot_key
    return DAY_ORDER.index(day), slot


def _schedule_sort_key(item: ScheduleItem) -> tuple[int, int, str, str]:
    return DAY_ORDER.index(item.day), item.slot, item.group, item.subject


def _unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))