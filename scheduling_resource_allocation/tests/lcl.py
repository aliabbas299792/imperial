import random
import pytest

from common.constants import CW_DAG_PATH
from common.models import DirectedAcyclicGraph
from algorithms.lcl import LowestCostLastScheduler


def generate_random_topological_schedule(dag: DirectedAcyclicGraph) -> list[int]:
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

    return random_schedule


@pytest.fixture
def dag():
    return DirectedAcyclicGraph.load_from_file(CW_DAG_PATH)


def test_lcl_schedule_cost(dag: DirectedAcyclicGraph):
    """
    Tests that the LCL schedule is at least as good as a random schedule
    Heuristically checks that the found LCL schedule really is optimal
    """

    scheduler = LowestCostLastScheduler(dag)
    schedule = scheduler.lcl()
    found_schedule_cost = scheduler.schedule_maximum_cost(schedule)

    costs = []
    for _ in range(10000):
        random_schedule = generate_random_topological_schedule(dag)
        costs.append(scheduler.schedule_maximum_cost(random_schedule))

    assert found_schedule_cost <= min(costs), (
        "Found schedule found to be less optimal than a randomly generated schedule"
        f"(LCL schedule cost: {found_schedule_cost}, minimum random cost: {min(costs)})"
    )
