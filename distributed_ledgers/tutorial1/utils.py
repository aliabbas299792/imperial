import gzip
import json
from pathlib import Path
from hashlib import sha256


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


def hash_pair(a: str, b: str) -> str:
    hash_str = a + b if a < b else b + a
    return "0x" + sha256(hash_str.encode()).hexdigest()


def pair_iter(lst):
    if len(lst) % 2 == 1:
        lst.append(None)

    for e1, e2 in zip(lst[::2], lst[1::2]):
        yield e1, e2


def enumerated_pair_iter(lst):
    if len(lst) % 2 == 1:
        lst.append(None)

    idxs = pair_iter(range(0, len(lst)))
    elems = pair_iter(lst)
    return zip(idxs, elems)
