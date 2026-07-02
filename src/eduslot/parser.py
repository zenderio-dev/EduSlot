import re
from typing import Literal

from eduslot.models import Day, TeacherAvailability, TeacherPreferenceInput, TimeSlot
from eduslot.time_grid import LESSON_TIMES, get_slots_for_day


TimeFilterMode = Literal["all", "between", "after", "before"]

DAY_ORDER: list[Day] = ["mon", "tue", "wed", "thu", "fri"]

DAY_ALIASES: dict[str, Day] = {
    "пн": "mon",
    "понедельник": "mon",
    "понедельника": "mon",
    "понедельникам": "mon",
    "вт": "tue",
    "вторник": "tue",
    "вторника": "tue",
    "вторникам": "tue",
    "ср": "wed",
    "среда": "wed",
    "среду": "wed",
    "среды": "wed",
    "средам": "wed",
    "чт": "thu",
    "четверг": "thu",
    "четверга": "thu",
    "четвергам": "thu",
    "пт": "fri",
    "пятница": "fri",
    "пятницу": "fri",
    "пятницы": "fri",
    "пятницам": "fri",
}

SLOT_WORDS: dict[str, int] = {
    "первая": 1,
    "первую": 1,
    "первой": 1,
    "вторая": 2,
    "вторую": 2,
    "второй": 2,
    "третья": 3,
    "третью": 3,
    "третьей": 3,
    "четвертая": 4,
    "четвертую": 4,
    "четвертой": 4,
    "пятая": 5,
    "пятую": 5,
    "пятой": 5,
}

DAY_PATTERN = "|".join(
    sorted(
        map(re.escape, DAY_ALIASES),
        key=len,
        reverse=True,
    )
)

SLOT_WORD_PATTERN = "|".join(
    sorted(
        map(re.escape, SLOT_WORDS),
        key=len,
        reverse=True,
    )
)


def parse_teacher_preference(teacher: str, text: str) -> TeacherAvailability:
    """Parse teacher preference text into available timetable slots."""
    normalized_text = _normalize_text(text)
    warnings: list[str] = []

    if not normalized_text:
        return TeacherAvailability(
            teacher=teacher,
            available_slots=[],
            warnings=["Пустой текст пожелания преподавателя."],
        )

    days = _extract_days(normalized_text)
    if not days:
        return TeacherAvailability(
            teacher=teacher,
            available_slots=[],
            warnings=["Не удалось определить день недели в пожелании преподавателя."],
        )

    specific_slots = _extract_specific_slots(normalized_text)

    if specific_slots:
        available_slots = _build_specific_slots(days, specific_slots)
    else:
        mode, start_time, end_time = _extract_time_filter(normalized_text)
        available_slots = _build_slots(days, mode, start_time, end_time)

    if not available_slots:
        warnings.append(
            "Не удалось сопоставить указанный временной интервал с сеткой занятий."
        )

    return TeacherAvailability(
        teacher=teacher,
        available_slots=available_slots,
        warnings=warnings,
    )


def parse_preference_input(preference: TeacherPreferenceInput) -> TeacherAvailability:
    """Parse one teacher preference input object."""
    return parse_teacher_preference(
        teacher=preference.teacher,
        text=preference.text,
    )


def _normalize_text(text: str) -> str:
    return text.strip().lower().replace("ё", "е")


def _extract_days(text: str) -> list[Day]:
    if "будни" in text or "по будням" in text:
        return DAY_ORDER.copy()

    days: set[Day] = set()

    dash_range_pattern = (
        rf"(?<![а-яa-z])({DAY_PATTERN})(?![а-яa-z])"
        r"\s*[-–—]\s*"
        rf"(?<![а-яa-z])({DAY_PATTERN})(?![а-яa-z])"
    )

    for start_alias, end_alias in re.findall(dash_range_pattern, text):
        start_day = DAY_ALIASES[start_alias]
        end_day = DAY_ALIASES[end_alias]
        days.update(_expand_day_range(start_day, end_day))

    word_range_pattern = (
        rf"с\s+({DAY_PATTERN})\s+по\s+({DAY_PATTERN})"
    )

    for start_alias, end_alias in re.findall(word_range_pattern, text):
        start_day = DAY_ALIASES[start_alias]
        end_day = DAY_ALIASES[end_alias]
        days.update(_expand_day_range(start_day, end_day))

    single_day_pattern = rf"(?<![а-яa-z])({DAY_PATTERN})(?![а-яa-z])"

    for day_alias in re.findall(single_day_pattern, text):
        days.add(DAY_ALIASES[day_alias])

    return [day for day in DAY_ORDER if day in days]


def _expand_day_range(start_day: Day, end_day: Day) -> list[Day]:
    start_index = DAY_ORDER.index(start_day)
    end_index = DAY_ORDER.index(end_day)

    if start_index > end_index:
        return []

    return DAY_ORDER[start_index : end_index + 1]


def _extract_specific_slots(text: str) -> list[int]:
    slots: set[int] = set()

    range_pattern = (
        r"(?<!\d)([1-8])\s*[-–—]\s*([1-8])\s*"
        r"(?:пара|пары|пар|паре|пару|парой)"
    )

    for start_slot, end_slot in re.findall(range_pattern, text):
        slots.update(_expand_slot_range(int(start_slot), int(end_slot)))

    single_number_pattern = (
        r"(?<!\d)([1-8])\s*"
        r"(?:пара|пары|пар|паре|пару|парой)"
    )

    for slot in re.findall(single_number_pattern, text):
        slots.add(int(slot))

    word_pattern = (
        rf"(?<![а-яa-z])({SLOT_WORD_PATTERN})(?![а-яa-z])\s+"
        r"(?:пара|пары|паре|пару|парой)"
    )

    for slot_word in re.findall(word_pattern, text):
        slots.add(SLOT_WORDS[slot_word])

    return sorted(slots)


def _expand_slot_range(start_slot: int, end_slot: int) -> list[int]:
    if start_slot > end_slot:
        return []

    return list(range(start_slot, end_slot + 1))


def _extract_time_filter(text: str) -> tuple[TimeFilterMode, str | None, str | None]:
    interval_match = re.search(
        r"с\s+(\d{1,2}(?::|\.)?\d{0,2})\s+до\s+(\d{1,2}(?::|\.)?\d{0,2})",
        text,
    )

    if interval_match:
        return (
            "between",
            _normalize_time(interval_match.group(1)),
            _normalize_time(interval_match.group(2)),
        )

    dash_interval_match = re.search(
        r"(?<!\d)(\d{1,2}(?::|\.)?\d{0,2})\s*[-–—]\s*"
        r"(\d{1,2}(?::|\.)?\d{0,2})(?!\d)",
        text,
    )

    if dash_interval_match:
        return (
            "between",
            _normalize_time(dash_interval_match.group(1)),
            _normalize_time(dash_interval_match.group(2)),
        )

    not_earlier_match = re.search(
        r"не\s+раньше\s+(\d{1,2}(?::|\.)?\d{0,2})",
        text,
    )
    if not_earlier_match:
        return "after", _normalize_time(not_earlier_match.group(1)), None

    not_later_match = re.search(
        r"не\s+позже\s+(\d{1,2}(?::|\.)?\d{0,2})",
        text,
    )
    if not_later_match:
        return "before", None, _normalize_time(not_later_match.group(1))

    after_match = re.search(r"после\s+(\d{1,2}(?::|\.)?\d{0,2})", text)
    if after_match:
        return "after", _normalize_time(after_match.group(1)), None

    before_match = re.search(r"до\s+(\d{1,2}(?::|\.)?\d{0,2})", text)
    if before_match:
        return "before", None, _normalize_time(before_match.group(1))

    if "утром" in text or "утро" in text:
        return "before", None, "12:30"

    if (
        "первая половина дня" in text
        or "первую половину дня" in text
        or "до обеда" in text
    ):
        return "before", None, "12:30"

    if (
        "вторая половина дня" in text
        or "вторую половину дня" in text
        or "после обеда" in text
        or "днем" in text
        or "день" in text
    ):
        return "after", "12:00", None

    if "вечером" in text or "вечер" in text:
        return "after", "15:30", None

    return "all", None, None


def _normalize_time(value: str) -> str:
    cleaned = value.replace(".", ":")

    if ":" in cleaned:
        hours, minutes = cleaned.split(":", maxsplit=1)
    else:
        hours, minutes = cleaned, "00"

    if minutes == "":
        minutes = "00"

    return f"{int(hours):02d}:{int(minutes):02d}"


def _build_specific_slots(days: list[Day], slots: list[int]) -> list[TimeSlot]:
    result: list[TimeSlot] = []

    for day in days:
        for slot in slots:
            if slot in LESSON_TIMES:
                result.append(TimeSlot(day=day, slot=slot))

    return result


def _build_slots(
    days: list[Day],
    mode: TimeFilterMode,
    start_time: str | None,
    end_time: str | None,
) -> list[TimeSlot]:
    result: list[TimeSlot] = []

    for day in days:
        if mode == "all":
            result.extend(get_slots_for_day(day))
            continue

        for slot_number, lesson_time in LESSON_TIMES.items():
            lesson_start = _time_to_minutes(lesson_time.start)
            lesson_end = _time_to_minutes(lesson_time.end)

            if mode == "between" and start_time and end_time:
                if (
                    lesson_start >= _time_to_minutes(start_time)
                    and lesson_end <= _time_to_minutes(end_time)
                ):
                    result.append(TimeSlot(day=day, slot=slot_number))

            if mode == "after" and start_time:
                if lesson_start >= _time_to_minutes(start_time):
                    result.append(TimeSlot(day=day, slot=slot_number))

            if mode == "before" and end_time:
                if lesson_end <= _time_to_minutes(end_time):
                    result.append(TimeSlot(day=day, slot=slot_number))

    return result


def _time_to_minutes(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)
