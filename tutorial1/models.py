import re
from typing import Annotated, TypeAlias, Iterator, ItemsView, KeysView, ValuesView
from pydantic import BaseModel, RootModel, ValidationInfo, PlainValidator

HEX_PATTERN = re.compile(r"^0x[A-Fa-f0-9]+$")


def validate_hex_str(value: str, _: ValidationInfo = None):
    if not HEX_PATTERN.match(value):
        raise ValueError(f"{value} isn't a valid hex string")
    return value


HexType: TypeAlias = Annotated[str, PlainValidator(validate_hex_str)]


class Header(BaseModel):
    difficulty: int
    height: int
    miner: HexType
    nonce: int
    hash: HexType
    previous_block_header_hash: HexType
    timestamp: int
    transactions_count: int
    transactions_merkle_root: HexType


class Transaction(BaseModel):
    amount: int
    lock_time: int
    receiver: HexType
    sender: HexType
    signature: str
    transaction_fee: int


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
    pass


class Mempool(ListRootModel[Transaction]):
    pass


class Accounts(DictRootModel[HexType, HexType]):
    pass
