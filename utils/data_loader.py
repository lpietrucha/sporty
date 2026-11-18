"""Read external test datasets from the data/ directory."""

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_test_data(file_name: str) -> dict[str, Any]:
    """Return the parsed JSON content of data/<file_name>."""
    return json.loads((DATA_DIR / file_name).read_text(encoding="utf-8"))
