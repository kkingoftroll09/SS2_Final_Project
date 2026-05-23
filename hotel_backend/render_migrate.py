from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    backend_dir = Path(__file__).resolve().parent
    os.chdir(backend_dir)

    subprocess.check_call([sys.executable, "-m", "alembic", "upgrade", "head"])


if __name__ == "__main__":
    main()
