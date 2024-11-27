from models.Schedule import Schedule
from models.DirectedAcyclicGraph import DirectedAcyclicGraph
from models.Node import Node


def tardiness_cost_fn(C_j: int, node: Node):
    return max(0, C_j - node.due_date)


def is_topologically_valid(schedule: Schedule, dag: DirectedAcyclicGraph) -> bool:
    position = {node: idx for idx, node in enumerate(schedule)}

    # check if all predecessors of every node in the schedule actually precedes that node
    for node in schedule:
        for predecessor in dag.reverse_adjacency_matrix.get(node, []):
            if position[predecessor] > position[node]:
                return False

    return True
