from models.Node import Node

def tardiness_cost_fn(C_j: int, node: Node):
    return max(0, C_j - node.due_date)