from nodes import InternalNode, LeafNode
from RoomCount import RoomCount

import numpy as np
from typing import cast, NamedTuple, Union, Tuple

SplitPoint = NamedTuple("SplitPoint", [("featureCol", int), ("value", float)])


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
