from loading import loadRawData
import numpy as np
import time
from typing import cast, NamedTuple

SplitPoint = NamedTuple("SplitPoint", [("featureCol", int), ("value", float)])


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

    def exactlyOneRoomPopulated(self) -> bool:
        return sum([1 if r >= 1 else 0 for r in self.roomCount]) == 1


def decisionTreeLearning(data: np.ndarray, depth: int = 0):
    if np.size(data) == 0:
        return

    count = countRoomLabelsInDataset(data)

    if count.exactlyOneRoomPopulated():
        return  # base case

    splitPoint = findSplit(data, count)

    splitCond = data[:, splitPoint.featureCol] < splitPoint.value
    leftDataset = data[splitCond]
    rightDataset = data[~splitCond]

    decisionTreeLearning(leftDataset, depth + 1)
    decisionTreeLearning(rightDataset, depth + 1)


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
            if featureCol[currIdx] == featureCol[nextIdx]:
                continue

            # mid point for splitting between sorted examples
            midpointVal = cast(float, np.mean(featureCol[[currIdx, nextIdx]]))
            roomNum = roomNums[currIdx]

            leftRoomsCount.decr(roomNum)
            rightRoomsCount.incr(roomNum)

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


def main():
    cleanData, noisyData = loadRawData()

    t1 = time.perf_counter()

    decisionTreeLearning(cleanData)

    t2 = time.perf_counter()
    print(t2 - t1)


if __name__ == "__main__":
    main()
