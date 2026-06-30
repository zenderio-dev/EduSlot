from eduslot.models import TeacherPreferenceInput, TimeSlot
from eduslot.parser import parse_preference_input, parse_teacher_preference


def test_parse_day_range_with_time_interval():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="ср-чт с 13:50 до 17:00",
    )

    assert availability.teacher == "Ivanov"
    assert availability.available_slots == [
        TimeSlot(day="wed", slot=4),
        TimeSlot(day="thu", slot=4),
    ]
    assert availability.warnings == []


def test_parse_single_day_first_half():
    availability = parse_teacher_preference(
        teacher="Petrov",
        text="в пятницу в первую половину дня",
    )

    assert availability.available_slots == [
        TimeSlot(day="fri", slot=1),
        TimeSlot(day="fri", slot=2),
    ]
    assert availability.warnings == []


def test_parse_multiple_days_after_time():
    availability = parse_teacher_preference(
        teacher="Sidorov",
        text="можно в понедельник и среду после 12:00",
    )

    assert availability.available_slots == [
        TimeSlot(day="mon", slot=3),
        TimeSlot(day="mon", slot=4),
        TimeSlot(day="mon", slot=5),
        TimeSlot(day="wed", slot=3),
        TimeSlot(day="wed", slot=4),
        TimeSlot(day="wed", slot=5),
    ]
    assert availability.warnings == []


def test_parse_single_day_without_time_returns_all_slots():
    availability = parse_teacher_preference(
        teacher="Smirnova",
        text="можно во вторник",
    )

    assert availability.available_slots == [
        TimeSlot(day="tue", slot=1),
        TimeSlot(day="tue", slot=2),
        TimeSlot(day="tue", slot=3),
        TimeSlot(day="tue", slot=4),
        TimeSlot(day="tue", slot=5),
    ]
    assert availability.warnings == []


def test_parse_preference_input_model():
    preference = TeacherPreferenceInput(
        teacher="Ivanov",
        text="среда до 12:30",
    )

    availability = parse_preference_input(preference)

    assert availability.teacher == "Ivanov"
    assert availability.available_slots == [
        TimeSlot(day="wed", slot=1),
        TimeSlot(day="wed", slot=2),
    ]


def test_text_without_weekday_returns_warning():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="можно после 12:00",
    )

    assert availability.available_slots == []
    assert availability.warnings == [
        "Не удалось определить день недели в пожелании преподавателя."
    ]


def test_empty_text_returns_warning():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="",
    )

    assert availability.available_slots == []
    assert availability.warnings == ["Пустой текст пожелания преподавателя."]


def test_interval_without_matching_lesson_returns_warning():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="понедельник с 07:00 до 08:00",
    )

    assert availability.available_slots == []
    assert availability.warnings == [
        "Не удалось сопоставить указанный временной интервал с сеткой занятий."
    ]
    