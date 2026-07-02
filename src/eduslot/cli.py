import argparse
import json
from pathlib import Path
from typing import Any

from eduslot import (
    generate_schedule,
    generate_schedule_variants,
    load_preferences,
    load_workload,
    summarize_schedule_metrics,
)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "solve":
        return _handle_solve(args)

    if args.command == "variants":
        return _handle_variants(args)

    if args.command == "metrics":
        return _handle_metrics(args)

    parser.print_help()
    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eduslot",
        description="EduSlot command-line interface.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser(
        "solve",
        help="Generate a schedule from workload and preferences JSON files.",
    )
    _add_common_arguments(solve_parser)

    variants_parser = subparsers.add_parser(
        "variants",
        help="Generate alternative schedule variants.",
    )
    _add_common_arguments(variants_parser)
    variants_parser.add_argument(
        "--max-variants",
        type=int,
        default=3,
        help="Maximum number of schedule variants to generate.",
    )

    metrics_parser = subparsers.add_parser(
        "metrics",
        help="Generate schedule and print summary metrics.",
    )
    _add_common_arguments(metrics_parser)

    return parser


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "workload_path",
        type=Path,
        help="Path to workload JSON file.",
    )
    parser.add_argument(
        "preferences_path",
        type=Path,
        help="Path to teacher preferences JSON file.",
    )
    parser.add_argument(
        "--max-time-seconds",
        type=float,
        default=10.0,
        help="Maximum solver time in seconds.",
    )


def _handle_solve(args: argparse.Namespace) -> int:
    workload = load_workload(args.workload_path)
    preferences = load_preferences(args.preferences_path)

    result = generate_schedule(
        workload=workload,
        preferences=preferences,
        max_time_seconds=args.max_time_seconds,
    )

    _print_json(result.model_dump(mode="json"))

    return 0 if not result.conflicts else 1


def _handle_variants(args: argparse.Namespace) -> int:
    workload = load_workload(args.workload_path)
    preferences = load_preferences(args.preferences_path)

    variants = generate_schedule_variants(
        workload=workload,
        preferences=preferences,
        max_variants=args.max_variants,
        max_time_seconds=args.max_time_seconds,
    )

    payload = {
        "variants": [
            variant.model_dump(mode="json")
            for variant in variants
        ]
    }

    _print_json(payload)

    has_conflicts = any(variant.conflicts for variant in variants)

    return 0 if not has_conflicts else 1


def _handle_metrics(args: argparse.Namespace) -> int:
    workload = load_workload(args.workload_path)
    preferences = load_preferences(args.preferences_path)

    result = generate_schedule(
        workload=workload,
        preferences=preferences,
        max_time_seconds=args.max_time_seconds,
    )
    metrics = summarize_schedule_metrics(result.schedule)

    payload = {
        "metrics": metrics.model_dump(mode="json"),
        "warnings": result.warnings,
        "conflicts": [
            conflict.model_dump(mode="json")
            for conflict in result.conflicts
        ],
    }

    _print_json(payload)

    return 0 if not result.conflicts else 1


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())