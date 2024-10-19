import numpy as np
from typing import Union, Optional

RoomLabel = int


class RoomCount:
    def __init__(self):
        self.roomCount = [0, 0, 0, 0]

    @staticmethod
    def getLabelFromIdx(idx: int) -> int:
        # roomNum labels are 1-indexed
        return idx + 1

    @staticmethod
    def getIdxFromLabel(label: Union[int, float]) -> int:
        # roomNum labels are 1-indexed, and loaded as floats
        return int(label - 1)

    def copyCount(self) -> "RoomCount":
        rc = RoomCount()
        rc.roomCount = self.roomCount[:]
        return rc

    def addRoomCount(self, roomNum: Union[int, float], incr: int) -> "RoomCount":
        idx = self.getIdxFromLabel(roomNum)
        self.roomCount[idx] += incr
        return self

    def incr(self, roomNum: int) -> "RoomCount":
        return self.addRoomCount(roomNum, 1)

    def decr(self, roomNum: int) -> "RoomCount":
        return self.addRoomCount(roomNum, -1)

    def totalRooms(self) -> int:
        return sum(self.roomCount)

    def entropy(self) -> float:
        total = self.totalRooms()

        # avoids divide by zero and signifies no uncertainty
        if total == 0:
            return 0

        return sum(
            [-p * np.log2(p) for p in [r / total for r in self.roomCount] if p != 0]
        )

    def weightedEntropy(self, supersetNumRooms) -> float:
        return self.entropy() * (self.totalRooms() / supersetNumRooms)

    def getLabelIfSingleRoomPopulated(self) -> Optional[RoomLabel]:
        seenRoom = False
        label = None
        for roomIdx, count in enumerate(self.roomCount):
            if not seenRoom and count != 0:
                seenRoom = True
                label = RoomLabel(self.getLabelFromIdx(roomIdx))
            elif seenRoom and count != 0:
                return None
        return label
