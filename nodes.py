import numpy as np


class LeafNode:
    def __init__(self, prediction):
        self.prediction = prediction
        self.node_type = "LEAF"

    def getPrediction(self):
        return self.prediction


class InternalNode:
    def __init__(self, split_criterion, split_attr):
        self.split_criterion = split_criterion
        self.split_attr = split_attr
        self.left = None
        self.right = None
        self.node_type = "INTERNAL"

    def evaluate(self, sample: np.ndarray):
        if sample[self.split_attr] <= self.split_criterion:
            if self.left.node_type == "LEAF":
                return self.left.getPrediction()
            else:
                return self.left.evaluate(sample)
        else:
            if self.right.node_type == "LEAF":
                return self.right.getPrediction()
            else:
                return self.right.evaluate(sample)

    def attach_left(self, node):
        self.left = node

    def attach_right(self, node):
        self.right = node

    def getLeft(self):
        return self.left

    def getRight(self):
        return self.right

    def getSplit(self):
        return self.split_criterion

    def getAttr(self):
        return self.split_attr


def printTree(node):
    if node.node_type == "LEAF":
        print("Leaf Node:", node.getPrediction())
    else:
        print("Internal Node:", node.getSplit())
        printTree(node.getRight())
        printTree(node.getLeft())
    return None
