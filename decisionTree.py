import numpy as np
from typing import cast, NamedTuple, Optional, Union, Tuple
from nodes import InternalNode, LeafNode

SplitPoint = NamedTuple("SplitPoint", [("featureCol", int), ("value", float)])
RoomLabel = int


class RoomCount:
    def __init__(self):
        self.roomCount = [0, 0, 0, 0]

    def copyCount(self) -> "RoomCount":
        rc = RoomCount()
        rc.roomCount = self.roomCount[:]
        return rc

    def addRoomCount(self, roomNum: int, incr: int) -> "RoomCount":
        idx = int(roomNum - 1)  # roomNum labels are 1-indexed, and loaded as floats
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
                label = RoomLabel(roomIdx + 1)  # back to 1-indexed
            elif seenRoom and count != 0:
                return None
        return label


def decisionTreeLearning(
    data: np.ndarray, depth: int = 0
) -> Tuple[Union[InternalNode, LeafNode], int]:
    count = countRoomLabelsInDataset(data)

    label = count.getLabelIfSingleRoomPopulated()
    if label != None:
        return LeafNode(label), depth

    splitPoint = findSplit(data, count)

    splitCond = data[:, splitPoint.featureCol] < splitPoint.value
    leftDataset = data[splitCond]
    rightDataset = data[~splitCond]

    nodeCentre = InternalNode(splitPoint.value, splitPoint.featureCol)
    nodeLeft, depthLeft = decisionTreeLearning(leftDataset, depth + 1)
    nodeRight, depthRight = decisionTreeLearning(rightDataset, depth + 1)

    nodeCentre.attach_left(nodeLeft)
    nodeCentre.attach_right(nodeRight)

    return nodeCentre, max(depthLeft, depthRight)


def findSplit(data: np.ndarray, roomCountParent: RoomCount) -> SplitPoint:
    roomNums = data.T[-1]
    parentEntropy = roomCountParent.entropy()
    totalRooms = roomCountParent.totalRooms()

    maxIG = 0
    maxIGSplit = None
    maxIGCol = None

    for colNum, featureCol in enumerate(data.T[:-1]):
        featureCol = cast(np.ndarray, featureCol)

        leftRoomsCount = roomCountParent.copyCount()
        rightRoomsCount = RoomCount()

        sortedIdxs = np.argsort(featureCol)
        for currIdx, nextIdx in zip(sortedIdxs, sortedIdxs[1:]):
            roomNum = roomNums[currIdx]

            leftRoomsCount.decr(roomNum)
            rightRoomsCount.incr(roomNum)

            if featureCol[currIdx] == featureCol[nextIdx]:
                continue

            # mid point for splitting between sorted examples
            midpointVal = cast(float, np.mean(featureCol[[currIdx, nextIdx]]))

            lWeightedEntr = leftRoomsCount.weightedEntropy(totalRooms)
            rWeightedEntr = rightRoomsCount.weightedEntropy(totalRooms)
            infoGain = parentEntropy - lWeightedEntr - rWeightedEntr

            if infoGain > maxIG:
                maxIG = infoGain
                maxIGSplit = midpointVal
                maxIGCol = colNum

    if maxIGCol == None or maxIGSplit == None:
        raise Exception("No valid split point found")

    return SplitPoint(maxIGCol, maxIGSplit)


def countRoomLabelsInDataset(data: np.ndarray) -> RoomCount:
    count = RoomCount()

    for row in data:
        roomNum = row[-1]
        count.incr(roomNum)

    return count
