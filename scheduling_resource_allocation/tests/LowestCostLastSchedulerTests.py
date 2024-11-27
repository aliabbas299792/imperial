import pytest

from common.constants import CW_DAG_PATH
from common.common import (
    is_topologically_valid,
    generate_random_tardy_topological_schedule,
)
from core.LowestCostLassScheduler import LowestCostLastScheduler
from models.TardySchedule import TardySchedule
from models.DirectedAcyclicGraph import DirectedAcyclicGraph


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
    assert is_topologically_valid(
        schedule, dag
    ), "LCL schedule is not topologically valid"
    found_schedule_cost = schedule.maximum_cost()

    costs = []
    for _ in range(10000):
        random_schedule = generate_random_tardy_topological_schedule(dag)
        assert is_topologically_valid(
            random_schedule, dag
        ), "Randomly generated schedule is not topologically valid"
        costs.append(random_schedule.maximum_cost())

    assert found_schedule_cost <= min(costs), (
        "Found schedule found to be less optimal than a randomly generated schedule"
        f"(LCL schedule cost: {found_schedule_cost}, minimum random cost: {min(costs)})"
    )
