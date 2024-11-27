import random
import pytest

from common.constants import CW_DAG_PATH
from core.LowestCostLassScheduler import LowestCostLastScheduler
from models.TardySchedule import TardySchedule
from models.DirectedAcyclicGraph import DirectedAcyclicGraph


def generate_random_tardy_topological_schedule(
    dag: DirectedAcyclicGraph,
) -> TardySchedule:
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

    return TardySchedule(random_schedule, dag)


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
    found_schedule_cost = schedule.maximum_cost()

    costs = []
    for _ in range(10000):
        random_schedule = generate_random_tardy_topological_schedule(dag)
        costs.append(random_schedule.maximum_cost())

    assert found_schedule_cost <= min(costs), (
        "Found schedule found to be less optimal than a randomly generated schedule"
        f"(LCL schedule cost: {found_schedule_cost}, minimum random cost: {min(costs)})"
    )
