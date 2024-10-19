import re
from typing import Annotated, TypeAlias, Iterator, ItemsView, KeysView, ValuesView
from pydantic import BaseModel, RootModel, PlainValidator, PlainSerializer

HEX_PATTERN = re.compile(r"^0x[A-Fa-f0-9]+$")


HexType: TypeAlias = Annotated[
    str,
    PlainValidator(lambda v: int(v, 16) if isinstance(v, str) else v),
    PlainSerializer(lambda v: hex(v if isinstance(v, int) else 0), return_type=str),
]


class Header(BaseModel):
    difficulty: int
    height: int
    miner: HexType
    nonce: int
    hash: HexType | None
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

    pass
