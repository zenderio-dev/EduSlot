# Input and output formats

EduSlot uses structured JSON input data and returns Pydantic models as output.

## Workload input

Workload input describes student groups and required weekly lessons.

Example:

```json
{
  "groups": [
    {
      "name": "Group A",
      "lessons": [
        {
          "subject": "Python",
          "teacher": "Ivanov",
          "lessons_per_week": 2,
          "lesson_type": "practice"
        },
        {
          "subject": "Databases",
          "teacher": "Petrov",
          "lessons_per_week": 2,
          "lesson_type": "lecture"
        }
      ]
    }
  ]
}
```

### Workload fields

| Field | Description |
| --- | --- |
| `groups` | List of student groups. |
| `name` | Group name. |
| `lessons` | List of lessons required for the group. |
| `subject` | Subject name. |
| `teacher` | Teacher name. |
| `lessons_per_week` | Required number of lessons per week. |
| `lesson_type` | Lesson type: `lecture`, `practice`, `lab` or `seminar`. |
| `consecutive_required` | Optional flag for future consecutive lesson logic. |
| `order_group` | Optional ordering group name. |
| `order_index` | Optional order index. |

## Teacher preferences input

Teacher preferences describe when teachers are available.

Example:

```json
{
  "preferences": [
    {
      "teacher": "Ivanov",
      "text": "понедельник и среда"
    },
    {
      "teacher": "Petrov",
      "text": "вторник и пятница"
    }
  ]
}
```

### Supported preference examples

| Text | Meaning |
| --- | --- |
| `понедельник и среда` | Teacher is available on Monday and Wednesday. |
| `ср-чт с 13:50 до 17:00` | Teacher is available from Wednesday to Thursday in the specified time range. |
| `пятница 1 пара` | Teacher is available on Friday during the first lesson slot. |
| `четверг 1-3 пары` | Teacher is available on Thursday during slots 1 to 3. |
| `по будням не раньше 14:00` | Teacher is available on weekdays after the specified time. |
| `с понедельника по среду после обеда` | Teacher is available from Monday to Wednesday in the second half of the day. |

## Schedule output

The main output type is `ScheduleResult`.

Example structure:

```json
{
  "schedule": [
    {
      "group": "Group A",
      "subject": "Python",
      "teacher": "Ivanov",
      "day": "mon",
      "slot": 1,
      "lesson_type": "practice"
    }
  ],
  "warnings": [],
  "conflicts": []
}
```

## Output fields

| Field | Description |
| --- | --- |
| `schedule` | List of generated schedule items. |
| `warnings` | Non-critical warnings produced during parsing or generation. |
| `conflicts` | Problems that prevented valid schedule generation or validation. |

## Schedule item fields

| Field | Description |
| --- | --- |
| `group` | Student group name. |
| `subject` | Subject name. |
| `teacher` | Teacher name. |
| `day` | Day code: `mon`, `tue`, `wed`, `thu`, `fri`. |
| `slot` | Lesson slot number. |
| `lesson_type` | Lesson type. |

## Export formats

EduSlot supports three export formats:

| Format | Purpose |
| --- | --- |
| JSON | Integration with other services and APIs. |
| CSV | Simple table format for quick review. |
| XLSX | Spreadsheet format for Excel or LibreOffice. |
