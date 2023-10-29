from loading import loadRawData
import numpy as np
from typing import cast, NamedTuple, Optional

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

vals = set()
def decisionTreeLearning(data: np.ndarray, alreadySplittedCols: set, depth: int = 0):
    if np.size(data) == 0:
        return
    
    count = countRoomLabelsInDataset(data)

    if count.exactlyOneRoomPopulated() or count.totalRooms() == 0:
        # print("base case")
        return

    splitPoint = findSplit(data, count, alreadySplittedCols)
        

    if not splitPoint:
        print('no valid split found')
        return
        # raise Exception("Split point was not found")

    if splitPoint.featureCol in alreadySplittedCols:
        print("haha!")
        print(alreadySplittedCols)
        return

    print(splitPoint.featureCol, splitPoint.value,)
    s = alreadySplittedCols.copy()
    s.add(splitPoint.featureCol)

    splitCond = data[:, splitPoint.featureCol] < splitPoint.value
    leftDataset = data[splitCond]
    rightDataset = data[~splitCond]

    global vals
    vals.add(splitPoint.value)
    # print("vals", len(vals))
    
    decisionTreeLearning(leftDataset, s, depth + 1)
    decisionTreeLearning(rightDataset, s, depth + 1)



def findSplit(data: np.ndarray, roomCountParent: RoomCount, excludeCols: set[int]) -> Optional[SplitPoint]:
    # assumes each row to be structured as such
    # [s1, s2, s3, s4, s5, s6, s7, roomNum]

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
        return None

    return SplitPoint(maxIGCol, maxIGSplit)


def countRoomLabelsInDataset(data: np.ndarray) -> RoomCount:
    count = RoomCount()

    for row in data:
        roomNum = row[-1]
        count.incr(roomNum)

    return count


import time
def main():
    cleanData, noisyData = loadRawData()
    t1 = time.perf_counter()
    # print("Clean Data Shape", cleanData.shape)
    # print("Noisy Data Shape", noisyData.shape)

    decisionTreeLearning(cleanData, set())
    t2 = time.perf_counter()
    print(t2 - t1)


if __name__ == "__main__":
    main()
