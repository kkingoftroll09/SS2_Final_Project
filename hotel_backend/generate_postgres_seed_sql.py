"""Generate a PostgreSQL data-only SQL dump for the hotel project tables.

This script reads data from a source database and writes PostgreSQL-compatible
INSERT statements in dependency order. Use it to move the current project data
from MySQL into a PostgreSQL database.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Iterable
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import MetaData, Table, create_engine, inspect, select
from sqlalchemy.dialects import postgresql

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import models  # noqa: F401,E402

TABLE_ORDER = [
    "room_type",
    "employee",
    "guest",
    "service",
    "room",
    "booking",
    "booking_detail",
    "payment",
    "booking_service",
    "housekeeping_task",
]
PG_DIALECT = postgresql.dialect()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export hotel project data as a PostgreSQL SQL script."
    )
    parser.add_argument(
        "--source-url",
        default=os.getenv("SOURCE_DATABASE_URL"),
        help="Source database URL. Defaults to SOURCE_DATABASE_URL.",
    )
    parser.add_argument(
        "--output",
        default="hotel_backend/postgres_data_dump.sql",
        help="Output SQL file path.",
    )
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Prepend TRUNCATE ... RESTART IDENTITY CASCADE so the dump can be replayed into a non-empty database.",
    )
    return parser.parse_args()


def resolve_url(value: str | None) -> str:
    if not value:
        raise SystemExit(
            "Missing SOURCE_DATABASE_URL. Set it or pass --source-url."
        )

    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg2://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg2://", 1)
    return value


def iter_common_tables(source_table_names: Iterable[str]) -> list[str]:
    available = set(source_table_names)
    return [table_name for table_name in TABLE_ORDER if table_name in available]


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def render_literal(column, value) -> str:
    if value is None:
        return "NULL"

    processor = column.type.literal_processor(PG_DIALECT)
    if processor is not None:
        rendered = processor(value)
        if rendered is not None:
            return rendered

    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, datetime):
        return f"'{value.isoformat(sep=' ', timespec='seconds')}'"
    if isinstance(value, date):
        return f"'{value.isoformat()}'"
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"

    return repr(value)


def export_table(source_conn, source_table, target_table) -> list[dict]:
    columns = [column.name for column in target_table.columns if column.name in source_table.c]
    if not columns:
        return []

    query = select(*(source_table.c[column_name] for column_name in columns))
    return [dict(row) for row in source_conn.execute(query).mappings().all()]


def render_insert(table_name: str, table, rows: list[dict]) -> str:
    if not rows:
        return ""

    columns = [column.name for column in table.columns if column.name in rows[0]]
    quoted_columns = ", ".join(quote_identifier(column_name) for column_name in columns)

    value_lines = []
    for row in rows:
        values = [render_literal(table.c[column_name], row[column_name]) for column_name in columns]
        value_lines.append("    (" + ", ".join(values) + ")")

    statement_lines = [
        f"INSERT INTO {quote_identifier(table_name)} ({quoted_columns}) VALUES",
        ",\n".join(value_lines) + ";",
    ]
    return "\n".join(statement_lines)


def render_sequence_reset(table_name: str, primary_key: str = "id") -> str:
    return (
        f"SELECT setval(pg_get_serial_sequence('{table_name}', '{primary_key}'), "
        f"COALESCE((SELECT MAX({quote_identifier(primary_key)}) FROM {quote_identifier(table_name)}), 1), true);"
    )


def main() -> None:
    args = parse_args()
    source_url = resolve_url(args.source_url)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    source_engine = create_engine(source_url)
    inspector = inspect(source_engine)
    source_tables = iter_common_tables(inspector.get_table_names())

    lines: list[str] = [
        "-- PostgreSQL data-only export for the hotel management project.",
        "-- Generate with SOURCE_DATABASE_URL pointing at MySQL, then run this file with psql.",
        "BEGIN;",
    ]

    if args.truncate:
        truncate_list = ", ".join(quote_identifier(table_name) for table_name in reversed(source_tables))
        lines.append(f"TRUNCATE TABLE {truncate_list} RESTART IDENTITY CASCADE;")

    with source_engine.connect() as source_conn:
        for table_name in source_tables:
            source_table = Table(table_name, MetaData(), autoload_with=source_conn)
            rows = export_table(source_conn, source_table, source_table)
            if not rows:
                continue

            lines.append(render_insert(table_name, source_table, rows))
            if any(column.name == "id" for column in source_table.columns):
                lines.append(render_sequence_reset(table_name))

    lines.append("COMMIT;")
    output_path.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote PostgreSQL data export to {output_path}")


if __name__ == "__main__":
    main()
