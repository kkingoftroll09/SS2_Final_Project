"""Migrate data from a MySQL database into PostgreSQL.

This utility copies the common hotel-management tables from a source MySQL
instance into the current PostgreSQL database, preserving primary-key values so
foreign-key relationships stay intact.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable

from sqlalchemy import MetaData, Table, create_engine, inspect, select, text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import Base  # noqa: E402
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy data from MySQL to PostgreSQL.")
    parser.add_argument(
        "--source-url",
        default=os.getenv("SOURCE_DATABASE_URL"),
        help="MySQL source database URL. Defaults to SOURCE_DATABASE_URL.",
    )
    parser.add_argument(
        "--target-url",
        default=os.getenv("DATABASE_URL"),
        help="PostgreSQL target database URL. Defaults to DATABASE_URL.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete target rows before copying so the import can be re-run.",
    )
    return parser.parse_args()


def resolve_url(value: str | None, label: str) -> str:
    if not value:
        raise SystemExit(f"Missing {label}. Set the environment variable or pass --{label.replace('_', '-')}")

    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg2://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg2://", 1)
    return value


def iter_common_tables(source_table_names: Iterable[str]) -> list[str]:
    available = set(source_table_names)
    return [table_name for table_name in TABLE_ORDER if table_name in available]


def copy_table(source_conn, target_conn, table_name: str) -> int:
    source_table = Table(table_name, MetaData(), autoload_with=source_conn)
    target_table = Table(table_name, MetaData(), autoload_with=target_conn)

    common_columns = [column.name for column in target_table.columns if column.name in source_table.c]
    if not common_columns:
        return 0

    query = select(*(source_table.c[column_name] for column_name in common_columns))
    rows = [dict(row) for row in source_conn.execute(query).mappings().all()]
    if rows:
        target_conn.execute(target_table.insert(), rows)
    return len(rows)


def reset_sequence(target_conn, table_name: str, primary_key: str = "id") -> None:
    sequence_name = target_conn.execute(
        text("SELECT pg_get_serial_sequence(:table_name, :column_name)"),
        {"table_name": table_name, "column_name": primary_key},
    ).scalar_one_or_none()

    if not sequence_name:
        return

    max_value = target_conn.execute(
        text(f'SELECT COALESCE(MAX("{primary_key}"), 0) FROM "{table_name}"')
    ).scalar_one()

    if max_value <= 0:
        return

    target_conn.execute(
        text("SELECT setval(:sequence_name, :max_value, true)"),
        {"sequence_name": sequence_name, "max_value": max_value},
    )


def main() -> None:
    args = parse_args()
    source_url = resolve_url(args.source_url, "source_url")
    target_url = resolve_url(args.target_url, "target_url")

    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)

    Base.metadata.create_all(bind=target_engine)

    source_tables = iter_common_tables(inspect(source_engine).get_table_names())

    with source_engine.connect() as source_conn, target_engine.begin() as target_conn:
        if args.replace:
            for table_name in reversed(source_tables):
                target_table = Table(table_name, MetaData(), autoload_with=target_conn)
                target_conn.execute(target_table.delete())

        for table_name in source_tables:
            copied_rows = copy_table(source_conn, target_conn, table_name)
            if copied_rows:
                reset_sequence(target_conn, table_name)
            print(f"Copied {copied_rows} row(s) from {table_name}")

    print("Migration complete.")


if __name__ == "__main__":
    main()
