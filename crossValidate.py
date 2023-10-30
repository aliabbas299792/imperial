from common import NUM_CROSS_VALIDATION_FOLDS, NUM_ROOMS
from decisionTree import decisionTreeLearning
from dataclasses import dataclass
from loading import loadRawData
from nodes import InternalNode

import numpy as np
import time


@dataclass
class ConfusionStats:
    accuracy: float = 0
    recall: float = 0
    precision: float = 0
    fScore: float = 0
    confusionMat: np.ndarray = np.array([])

    def __str__(self) -> str:
        indentedStrMat = "\t\t" + str(self.confusionMat).replace("\n", "\n\t\t")
        return (
            f"\n\t-> Accuracy: {self.accuracy}"
            f"\n\t-> Precision: {self.precision}"
            f"\n\t-> Recall: {self.recall}"
            f"\n\t-> F1-score: {self.fScore}"
            f"\n\t-> Confusion Matrix:\n{indentedStrMat}"
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

    stats = ConfusionStats()
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

        stats.accuracy += (
            (truePos + trueNeg) / (truePos + trueNeg + falsePos + falseNeg)
        ) / classes
        stats.precision += (truePos / (truePos + falsePos)) / classes
        stats.recall += (truePos / (truePos + falseNeg)) / classes
        stats.fScore += (
            2 * ((stats.precision * stats.recall) / (stats.precision + stats.recall))
        ) / classes

    stats.confusionMat = confusionMat
    return stats


def generateFolds(data: np.ndarray, numFolds: int = 10) -> ConfusionStats:
    return np.split(data, numFolds)


def crossValidate(data: np.ndarray):
    folds = generateFolds(data, NUM_CROSS_VALIDATION_FOLDS)

    confusionMats = []
    for i, testData in enumerate(folds):
        trainData = np.concatenate([fold for j, fold in enumerate(folds) if j != i])
        decisionTree, _ = decisionTreeLearning(trainData)

        confusionMats.append(evaluation(testData, decisionTree))

    overallConfusionMat = np.sum(confusionMats, axis=0)
    return confusionStats(overallConfusionMat)


def main():
    startTime = time.perf_counter()

    cleanData, noisyData = loadRawData()

    statsClean = crossValidate(cleanData)
    statsNoisy = crossValidate(noisyData)

    print(f"Clean stats: {statsClean}")
    print(f"Noisy stats: {statsNoisy}")
    print(f"Time elapsed: {time.perf_counter() - startTime}s")
    print(f"For {NUM_CROSS_VALIDATION_FOLDS} folds")


if __name__ == "__main__":
    main()
