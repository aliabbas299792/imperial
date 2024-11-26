from itertools import accumulate
from typing import Callable

from common.models import DirectedAcyclicGraph

IterationCallback = Callable[
    [set[int], int, int, int, list[int]], None
]  # available jobs/successor set, p(N), p(N - {j}), scheduled job id j, partial schedule


def tardiness_cost_fn(C_j: int, d_j: int):
    return max(0, C_j - d_j)


class LowestCostLastScheduler:
    def __init__(self, dag: DirectedAcyclicGraph):
        self._dag = dag

    def schedule_completion_times(self, schedule: list[int]) -> list[int]:
        return list(
            accumulate([self._dag.node_processing_time(n_id) for n_id in schedule])
        )

    def schedule_tardiness(
        self, schedule: list[int], starting_time: int = 0
    ) -> list[int]:
        completion_times = [
            starting_time + C_j for C_j in self.schedule_completion_times(schedule)
        ]
        return [
            tardiness_cost_fn(C_j, self._dag.nodes[n_id].due_date)
            for n_id, C_j in zip(schedule, completion_times)
        ]

    def schedule_maximum_cost(self, schedule: list[int], starting_time: int = 0) -> int:
        return max(self.schedule_tardiness(schedule, starting_time))

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
            key=lambda n_id: tardiness_cost_fn(
                cumulative_cost, self._dag.nodes[n_id].due_date
            ),
        )

    def lcl(self, callback: IterationCallback | None = None) -> list[int]:
        """
        Constructs an LCL schedule for a given DAG
        """

        running_out_degs = self._dag.node_out_degrees.copy()
        cumulative_cost = sum(
            self._dag.node_processing_time(n_id) for n_id in self._dag.nodes
        )
        successorless = {
            n for n in self._dag.nodes if self._dag.node_out_degrees[n] == 0
        }

        reverse_schedule = []
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
                callback(
                    previous_successorless,
                    cumulative_cost,
                    new_cumulative_cost,
                    scheduled,
                    reverse_schedule[::-1],
                )

            cumulative_cost = new_cumulative_cost

        return reverse_schedule[::-1]
