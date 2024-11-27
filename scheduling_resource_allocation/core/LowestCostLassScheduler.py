from typing import Callable

from common.common import tardiness_cost_fn
from models.Schedule import Schedule
from models.TardySchedule import TardySchedule
from models.DirectedAcyclicGraph import DirectedAcyclicGraph

IterationCallback = Callable[
    [set[int], int, int, int, Schedule], None
]  # available jobs/successor set, p(N), p(N - {j}), scheduled job id j, partial schedule


class LowestCostLastScheduler:
    def __init__(self, dag: DirectedAcyclicGraph):
        self._dag = dag

    def update_successorless_nodes(
        self,
        newly_scheduled_job: int,
        running_out_degs: dict[int, int],
        successorless_nodes: set[int],
    ):
        for parent in self._dag.reverse_adjacency_matrix[newly_scheduled_job]:
            running_out_degs[parent] -= 1
            if running_out_degs[parent] == 0:
                successorless_nodes.add(parent)

    def select_minimising_job(
        self, cumulative_cost: int, successorless_nodes: set[int]
    ):
        return min(
            successorless_nodes,
            key=lambda n_id: tardiness_cost_fn(cumulative_cost, self._dag.nodes[n_id]),
        )

    def lcl(self, callback: IterationCallback | None = None) -> Schedule:
        """
        Constructs an LCL schedule for a given DAG
        """

        schedule = TardySchedule([], self._dag)

        running_out_degs = self._dag.node_out_degrees.copy()
        cumulative_cost = sum(
            self._dag.node_processing_time(n_id) for n_id in self._dag.nodes
        )
        successorless = {
            n for n in self._dag.nodes if self._dag.node_out_degrees[n] == 0
        }

        reverse_schedule = []
        iteration = 0
        while successorless:
            scheduled = None
            previous_successorless = successorless.copy()

            if len(successorless) == 1:
                scheduled = successorless.pop()
            else:
                scheduled = self.select_minimising_job(cumulative_cost, successorless)
                successorless.remove(scheduled)

            new_cumulative_cost = cumulative_cost - self._dag.node_processing_time(
                scheduled
            )
            reverse_schedule.append(scheduled)

            self.update_successorless_nodes(
                newly_scheduled_job=scheduled,
                running_out_degs=running_out_degs,
                successorless_nodes=successorless,
            )

            if callback is not None:
                schedule.set_schedule(reverse_schedule[::-1])
                callback(
                    previous_successorless,
                    cumulative_cost,
                    new_cumulative_cost,
                    scheduled,
                    schedule,
                )

            cumulative_cost = new_cumulative_cost
            iteration += 1
            
            print(f"Iteration: {iteration}\n\t -> Current solution: {reverse_schedule[::-1]}\n\t -> Cost: {cumulative_cost}")

        schedule.set_schedule(reverse_schedule[::-1])
        return TardySchedule(reverse_schedule[::-1], self._dag)
