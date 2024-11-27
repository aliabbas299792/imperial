from common.common import tardiness_cost_fn
from models.Schedule import Schedule
from models.DirectedAcyclicGraph import DirectedAcyclicGraph


class TardySchedule(Schedule):
    def __init__(self, schedule: list[int], dag: DirectedAcyclicGraph):
        super().__init__(schedule, dag, tardiness_cost_fn)
