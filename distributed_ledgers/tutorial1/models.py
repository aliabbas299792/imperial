import re
import ecdsa
from hashlib import sha256
from typing import Annotated, TypeAlias, Iterator, ItemsView, KeysView, ValuesView
import ecdsa.util
from pydantic import BaseModel, RootModel, PlainValidator

from utils import to_hex, from_hex


HEX_PATTERN = re.compile(r"^0x[A-Fa-f0-9]+$")


def validate_hex(s):
    if not re.fullmatch(HEX_PATTERN, s):
        raise ValueError("Invalid Hex string")
    return s


HexType: TypeAlias = Annotated[
    str,
    PlainValidator(validate_hex),
]


class HashableModel(BaseModel):
    def serialise(self, fields_to_exclude: list = None) -> str:
        fields_to_exclude = set(fields_to_exclude or [])
        fields_sorted_by_key = sorted(self.model_dump().items())
        values = [str(v) for k, v in fields_sorted_by_key if k not in fields_to_exclude]
        return ",".join(values)

    def compute_model_hash(self, fields_to_exclude: list = None) -> bytes:
        serialised = self.serialise(fields_to_exclude)
        hashed = sha256(serialised.encode()).digest()
        return hashed

    def compute_model_hash_hex(self, fields_to_exclude: list = None) -> str:
        return to_hex(self.compute_model_hash(fields_to_exclude))


class Header(HashableModel):
    difficulty: int
    height: int
    miner: HexType
    nonce: int
    hash: HexType | None
    previous_block_header_hash: HexType
    timestamp: int
    transactions_count: int
    transactions_merkle_root: HexType


class Transaction(HashableModel):
    amount: int
    lock_time: int
    receiver: HexType
    sender: HexType
    signature: str | None
    transaction_fee: int

    def compute_transaction_hash(self):
        return self.compute_model_hash(fields_to_exclude=["signature"])

    def compute_transaction_hash_hex(self):
        return to_hex(self.compute_transaction_hash())

    def sign(self, private_key: ecdsa.SigningKey):
        hash_to_sign = self.compute_transaction_hash()
        hex_signed_hash = private_key.sign_digest(
            hash_to_sign, sigencode=ecdsa.util.sigencode_der
        )
        public_key = private_key.verifying_key
        der_hex_pub_key = to_hex(public_key.to_der())
        full_signature = f"{der_hex_pub_key},{to_hex(hex_signed_hash)}"
        self.signature = full_signature

    def verify_signature(self) -> bool:
        if not self.signature:
            return False

        der_hex_pub_key, hex_signed_hash = self.signature.split(",")
        pub_key = ecdsa.VerifyingKey.from_der(from_hex(der_hex_pub_key))

        try:
            return pub_key.verify_digest(
                from_hex(hex_signed_hash),
                self.compute_transaction_hash(),
                sigdecode=ecdsa.util.sigdecode_der,
            )
        except ecdsa.BadSignatureError:
            return False  # invalid transaction if anything failed


class Block(BaseModel):
    header: Header
    transactions: list[Transaction]


class ContainerRootModel[Container, IdxType, ValType](RootModel[Container]):
    def __getitem__(self, index: IdxType) -> ValType:
        return self.root[index]

    def __setitem__(self, index: IdxType, value: ValType) -> None:
        self.root[index] = value

    def __delitem__(self, index: IdxType) -> None:
        del self.root[index]

    def __iter__(self) -> Iterator:
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)


class ListRootModel[T](ContainerRootModel[list[T], int, T]):
    def append(self, value: T) -> None:
        self.root.append(value)


class DictRootModel[K, V](ContainerRootModel[dict[K, V], K, V]):
    def items(self) -> ItemsView[K, V]:
        return self.root.items()

    def keys(self) -> KeysView[K]:
        return self.root.keys()

    def values(self) -> ValuesView[V]:
        return self.root.values()


class Blockchain(ListRootModel[Block]):
    """
    A list of `Block` objects
    """

    pass


class Mempool(ListRootModel[Transaction]):
    """
    A list of `Transaction` objects
    """

    pass


class Accounts(DictRootModel[HexType, HexType]):
    """
    A dictionary which maps account numbers, to their private keys
    """

    def get_as_private_key(self, account: HexType) -> ecdsa.SigningKey:
        return ecdsa.SigningKey.from_der(from_hex(self[account]))
