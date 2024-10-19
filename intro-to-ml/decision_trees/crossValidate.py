from common import (
    NUM_CROSS_VALIDATION_FOLDS,
    NUM_ROOMS,
    DEFAULT_CLEAN_DATASET_PATH,
    DEFAULT_NOISY_DATASET_PATH,
    loadRawData,
)
from RoomCount import RoomCount
from decisionTree import decisionTreeLearning
from dataclasses import dataclass, field
from nodes import InternalNode

import numpy as np
import time


@dataclass
class RoomConfusionStats:
    roomLabel: int = 0
    recall: float = 0
    precision: float = 0
    fScore: float = 0


@dataclass
class ConfusionStats:
    accuracy: float = 0
    roomConfusionStats: list[RoomConfusionStats] = field(default_factory=list)
    confusionMat: np.ndarray = np.array([])

    def __str__(self) -> str:
        prefix = "\n\t->"
        indentedStrMat = "\t\t" + str(self.confusionMat).replace("\n", "\n\t\t")
        roomStats = prefix + prefix.join(
            [str(roomStat) for roomStat in self.roomConfusionStats]
        )
        return (
            f"{prefix} Accuracy: {self.accuracy}"
            f"{roomStats}"
            f"{prefix} Confusion Matrix:\n{indentedStrMat}"
        )


def evaluation(testData: np.ndarray, decisionTree: InternalNode) -> np.ndarray:
    actual = testData[:, -1].astype(dtype=int)
    totalLabels = NUM_ROOMS
    predicted = [int(decisionTree.evaluate(row)) for row in testData]
    confusionMat = np.zeros((totalLabels, totalLabels))

    for trueLabel, predictedLabel in zip(actual, predicted):
        confusionMat[trueLabel - 1][predictedLabel - 1] += 1

    return confusionMat


def confusionStats(confusionMat: np.ndarray) -> ConfusionStats:
    classes = NUM_ROOMS

    accuracy = 0
    classConfusionStatsList = []

    for i in range(classes):
        truePos = confusionMat[i][i]
        trueNeg = 0
        falsePos = 0
        falseNeg = 0

        for actualIdx in range(classes):
            for predictIdx in range(classes):
                predictions = confusionMat[actualIdx][predictIdx]
                if actualIdx != i and predictIdx != i:
                    trueNeg += predictions
                elif predictIdx == i and actualIdx != i:
                    falsePos += predictions
                elif actualIdx == i and predictIdx != i:
                    falseNeg += predictions

        accuracy += (truePos + trueNeg) / (truePos + trueNeg + falsePos + falseNeg)

        confusionStats = RoomConfusionStats()
        confusionStats.precision = truePos / (truePos + falsePos)
        confusionStats.recall = truePos / (truePos + falseNeg)
        confusionStats.fScore = (
            2 * confusionStats.precision * confusionStats.recall
        ) / (confusionStats.precision + confusionStats.recall)

        confusionStats.roomLabel = RoomCount.getLabelFromIdx(i)

        classConfusionStatsList.append(confusionStats)

    accuracy /= classes

    return ConfusionStats(accuracy, classConfusionStatsList, confusionMat)


def generateFolds(data: np.ndarray, numFolds: int = 10) -> ConfusionStats:
    return np.split(data, numFolds)


def crossValidate(data: np.ndarray):
    folds = generateFolds(data, NUM_CROSS_VALIDATION_FOLDS)

    confusionMats = []
    for i, testData in enumerate(folds):
        trainData = np.concatenate([fold for j, fold in enumerate(folds) if j != i])
        decisionTree, _ = decisionTreeLearning(trainData)

        confusionMats.append(evaluation(testData, decisionTree))

    overallConfusionMat = np.sum(confusionMats, axis=0) / NUM_CROSS_VALIDATION_FOLDS
    return confusionStats(overallConfusionMat)


def crossValidateDataset(dataset: np.ndarray):
    startTime = time.perf_counter()

    stats = crossValidate(dataset)

    print(f"Decision tree stats: {stats}")
    print(f"Time elapsed: {time.perf_counter() - startTime}s")

    print(f"For {NUM_CROSS_VALIDATION_FOLDS} folds")


if __name__ == "__main__":
    cleanDataset = loadRawData(DEFAULT_CLEAN_DATASET_PATH)
    noisyDataset = loadRawData(DEFAULT_NOISY_DATASET_PATH)

    print("Clean dataset stuff:")
    crossValidateDataset(cleanDataset)
    print("")
    print("Noisy dataset stuff:")
    crossValidateDataset(noisyDataset)
