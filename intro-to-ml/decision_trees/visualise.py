from common import loadRawData, DEFAULT_CLEAN_DATASET_PATH
from decisionTree import decisionTreeLearning

import time
import numpy as np
import matplotlib.pyplot as plt


def plot_tree(node, ax, x=300, y=300, depth=0):
    # Calculate dynamic offsets based on depth
    hx = 300 / (2**depth + 2)
    hy = 20
    size = 0

    if hx > 150:
        size = 8
    elif hx > 100:
        size = 7
    elif hx > 50:
        size = 5
    elif hx > 25:
        size = 4
    else:
        size = 3

    if node.node_type == "LEAF":
        ax.text(
            x,
            y,
            int(node.getPrediction()),
            color="white",
            bbox=dict(boxstyle="round", facecolor="green", edgecolor="green"),
            zorder=10,
            fontsize=size,
        )
    else:
        ax.text(
            x,
            y,
            f"X{str(node.getAttr())}<{float(node.getSplit())}",
            color="red",
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="red"),
            zorder=10,
            fontsize=size,
            horizontalalignment="center",
        )

        # if the horizontal offset is too small, I increase the vertical offset (just to be sure of no overlap) and then increase the horizonal offset

        while hx < 5:
            hx = hx * 10
            hy = 30

        plt.arrow(x, y, -hx, -hy, zorder=0)
        plt.arrow(x, y, hx, -hy, zorder=0)
        plot_tree(node.getLeft(), ax, x - hx, y - hy, depth + 1)
        plot_tree(node.getRight(), ax, x + hx, y - hy, depth + 1)


def generateVisualisations(dataset: np.ndarray):
    startTime = time.perf_counter()

    node, depth = decisionTreeLearning(dataset)

    fig, ax = plt.subplots()
    plot_tree(node, ax)
    print(f"The maximum depth of the tree was: {depth}")
    print(f"Time elapsed: {time.perf_counter() - startTime}s")

    plt.axis("off")
    plt.savefig("tree.png", dpi=1200)
    plt.show()


if __name__ == "__main__":
    # when run from here will only show visualisation from the clean dataset
    # for more options use tool.py
    cleanDataset = loadRawData(DEFAULT_CLEAN_DATASET_PATH)
    generateVisualisations(cleanDataset)
