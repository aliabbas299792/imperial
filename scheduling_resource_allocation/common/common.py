import random

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


def generate_random_tardy_topological_schedule(
    dag: DirectedAcyclicGraph,
) -> Schedule:
    in_degrees = dag.node_in_degrees.copy()
    predecessorless = [n for n in dag.nodes if dag.node_in_degrees[n] == 0]
    random_schedule = []

    while predecessorless:
        selected_node = random.choice(predecessorless)
        random_schedule.append(selected_node)
        predecessorless.remove(selected_node)

        for child in dag.adjacency_matrix.get(selected_node, []):
            in_degrees[child] -= 1
            if in_degrees[child] == 0:
                predecessorless.append(child)

    return Schedule(random_schedule, dag, tardiness_cost_fn)
