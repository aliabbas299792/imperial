from typing import Callable
from itertools import accumulate

from common.models import DirectedAcyclicGraph, Node
from common.common import tardiness_cost_fn

# (completion_time: int, node: Node) -> (cost: int)
CostFn = Callable[[int, Node], int]

class Schedule:
    def __init__(self, schedule: list[int], dag: DirectedAcyclicGraph, cost_fn: CostFn):
        self._schedule = schedule
        self._dag = dag
        self._cost_fn = cost_fn
        
    def set_schedule(self, schedule: list[int]):
        self._schedule = schedule
      
    def maximum_cost(self, starting_time: int = 0) -> int:
      return max(self.costs(starting_time))
      
    def completion_times(self) -> list[int]:
        return list(
            accumulate([self._dag.node_processing_time(n_id) for n_id in self._schedule])
        )
      
    def costs(self, starting_time: int = 0) -> list[int]:
            completion_times = [
                starting_time + C_j for C_j in self.completion_times()
            ]
            
            return [
                self._cost_fn(C_j, self._dag.nodes[n_id])
                for n_id, C_j in zip(self._schedule, completion_times)
            ]

    def __str__(self) -> str:
        return str(self._schedule)
            
class TardySchedule(Schedule):
    def __init__(self, schedule: list[int], dag: DirectedAcyclicGraph):
        super().__init__(schedule, dag, tardiness_cost_fn)