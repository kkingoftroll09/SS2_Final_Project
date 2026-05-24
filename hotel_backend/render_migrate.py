from __future__ import annotations

from db import Base, engine
import models  # noqa: F401


def main() -> None:
    # Render PostgreSQL deploys should create the schema directly from the ORM
    # models so we don't depend on the old MySQL-specific Alembic revisions.
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    main()
