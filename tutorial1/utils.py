import gzip
import json
from pathlib import Path


def load_json_gz(path: Path) -> list | dict:
    with gzip.open(path, "rt") as f:
        return json.load(f)
