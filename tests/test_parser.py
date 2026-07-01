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


def test_parse_teacher_preference_supports_weekday_range_with_words():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="можно с понедельника по среду после обеда",
    )

    assert availability.warnings == []
    assert [(slot.day, slot.slot) for slot in availability.available_slots] == [
        ("mon", 3),
        ("mon", 4),
        ("mon", 5),
        ("tue", 3),
        ("tue", 4),
        ("tue", 5),
        ("wed", 3),
        ("wed", 4),
        ("wed", 5),
    ]


def test_parse_teacher_preference_supports_workdays():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="по будням не раньше 14:00",
    )

    assert availability.warnings == []
    assert [(slot.day, slot.slot) for slot in availability.available_slots] == [
        ("mon", 4),
        ("mon", 5),
        ("tue", 4),
        ("tue", 5),
        ("wed", 4),
        ("wed", 5),
        ("thu", 4),
        ("thu", 5),
        ("fri", 4),
        ("fri", 5),
    ]


def test_parse_teacher_preference_supports_morning_phrase():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="пн, ср, пт утром",
    )

    assert availability.warnings == []
    assert [(slot.day, slot.slot) for slot in availability.available_slots] == [
        ("mon", 1),
        ("mon", 2),
        ("wed", 1),
        ("wed", 2),
        ("fri", 1),
        ("fri", 2),
    ]


def test_parse_teacher_preference_supports_evening_phrase():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="четверг вечером",
    )

    assert availability.warnings == []
    assert [(slot.day, slot.slot) for slot in availability.available_slots] == [
        ("thu", 5),
    ]


def test_parse_teacher_preference_supports_dash_time_interval():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="среда 09:00-12:30",
    )

    assert availability.warnings == []
    assert [(slot.day, slot.slot) for slot in availability.available_slots] == [
        ("wed", 1),
        ("wed", 2),
    ]


def test_parse_teacher_preference_supports_not_later_phrase():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="вторник не позже 12:30",
    )

    assert availability.warnings == []
    assert [(slot.day, slot.slot) for slot in availability.available_slots] == [
        ("tue", 1),
        ("tue", 2),
    ]


def test_parse_teacher_preference_supports_lesson_slot_number():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="пятница 1 пара",
    )

    assert availability.warnings == []
    assert [(slot.day, slot.slot) for slot in availability.available_slots] == [
        ("fri", 1),
    ]


def test_parse_teacher_preference_supports_lesson_slot_range():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="четверг 1-3 пары",
    )

    assert availability.warnings == []
    assert [(slot.day, slot.slot) for slot in availability.available_slots] == [
        ("thu", 1),
        ("thu", 2),
        ("thu", 3),
    ]


def test_parse_teacher_preference_supports_lesson_slot_word():
    availability = parse_teacher_preference(
        teacher="Ivanov",
        text="понедельник первая пара",
    )

    assert availability.warnings == []
    assert [(slot.day, slot.slot) for slot in availability.available_slots] == [
        ("mon", 1),
    ]
    