import gzip
import json
from hashlib import sha256
from pathlib import Path
from pydantic import BaseModel


def load_json_gz(path: Path) -> list | dict:
    with gzip.open(path, "rt") as f:
        return json.load(f)


def model_hash(model: BaseModel):
    fields_sorted_by_key = sorted(model.model_dump().items())
    values = ",".join([str(v) for _, v in fields_sorted_by_key])
    hashed = sha256(values.encode()).hexdigest()
    return hashed
