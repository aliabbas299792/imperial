import gzip
import json
from pathlib import Path


def load_json_gz(path: Path) -> list | dict:
    with gzip.open(path, "rt") as f:
        return json.load(f)


def save_json_gz(path: Path, obj: list | dict) -> None:
    with gzip.open(path, "wt") as f:
        json.dump(obj, f)


def from_hex(hex_string: str) -> bytes:
    return bytes.fromhex(hex_string[2:])


def to_hex(b: bytes) -> str:
    return "0x" + b.hex()
