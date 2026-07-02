# Limitations

EduSlot is a scheduling library prototype focused on automatic timetable generation for educational groups.

## Not a complete university system

EduSlot does not provide:

- user accounts;
- role management;
- database storage;
- schedule history;
- manual schedule editing;
- web backend API;
- authentication;
- teacher or student portals.

These responsibilities should be handled by an external system that integrates EduSlot as a scheduling engine.

## Stateless behavior

EduSlot does not remember previous schedules. It receives input data, generates a schedule result and returns it to the caller.

If an external service needs history, versioning or manual approval workflow, it should store generated results separately.

## Input format

EduSlot expects structured input data. It does not generate a complete timetable from free-form text alone.

Teacher preferences may be written as short natural-language descriptions, but workload data must be provided in a structured JSON format.

## Teacher preference parser

The preference parser supports common Russian phrases for days, time ranges and lesson numbers.

It is not a full natural-language understanding system. Complex requests such as schedule edits, replacements or multi-condition rules should be implemented in an external service or future parser extension.

## Time grid

The current timetable grid is fixed inside the project.

Different universities may use different lesson times, number of slots and working days. A configurable time grid can be added as a future improvement.

## Solver constraints

The current solver supports core hard constraints:

- one teacher cannot teach several lessons in the same slot;
- one group cannot attend several lessons in the same slot;
- teacher availability must be respected;
- each lesson unit must be assigned to one slot.

More advanced constraints can be added later, for example room capacity, building distance, teacher workload balancing or preferred lesson distribution.

## Streamlit interface

The Streamlit interface is a demo layer for project presentation. It is not required for using EduSlot as a Python library.

## Future improvements

Possible future improvements:

- configurable time grid;
- classroom and room capacity support;
- stronger optimization criteria;
- deterministic solver settings;
- richer natural-language preference parser;
- FastAPI wrapper for web integration;
- database integration examples;
- published hosted documentation.
