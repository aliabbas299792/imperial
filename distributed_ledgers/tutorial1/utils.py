import gzip
import json
from hashlib import sha256
from pathlib import Path
from pydantic import BaseModel


def load_json_gz(path: Path) -> list | dict:
    with gzip.open(path, "rt") as f:
        return json.load(f)


def save_json_gz(path: Path, obj: list | dict) -> None:
    with gzip.open(path, "wt") as f:
        json.dump(obj, f)


def model_hash(model: BaseModel, fields_to_exclude: list = None):
    if not fields_to_exclude:
        fields_to_exclude = set()
    else:
        fields_to_exclude = set(fields_to_exclude)

    fields_sorted_by_key = sorted(model.model_dump().items())
    values = ",".join(
        [str(v) for k, v in fields_sorted_by_key if k not in fields_to_exclude]
    )
    hashed = sha256(values.encode()).hexdigest()
    return hashed
