from typing import Callable

from models.DirectedAcyclicGraph import DirectedAcyclicGraph
from models.Node import Node
from models.Schedule import Schedule

# (iteration, candidate schedules, total costs, tabu list, best cost, was tabu list used, best neighbour | None) -> None
IterationCallback = Callable[
    [int, list[Schedule], int, list[tuple[int, int]], int, bool], None
]


class TabuSearchScheduler:
    def __init__(
        self,
        dag: DirectedAcyclicGraph,
        tabu_length: int,
        max_iterations: int,
        gamma: int,
    ):
        self._dag = dag
        self._tabu_length = tabu_length  # L in the slides
        self._max_iterations = max_iterations  # K in the slides
        self._gamma = gamma  # gamma in the slides
        self._last_start_index = 0

    def is_swap_valid(self, node_a: Node, node_b: Node, schedule: Schedule) -> bool:
        """
        Checks if a swap between two nodes respects the topological constraints of the DAG
        It checks if the predecessors of node_a are before node_b, and the successors of node_a after node_b,
          and the same for node_b
        """
        position = {node: idx for idx, node in enumerate(schedule)}

        for predecessor in self._dag.reverse_adjacency_matrix.get(node_a, []):
            if position[predecessor] > position[node_b]:
                return False

        for predecessor in self._dag.reverse_adjacency_matrix.get(node_b, []):
            if position[predecessor] > position[node_a]:
                return False

        for successor in self._dag.adjacency_matrix.get(node_a, []):
            if position[successor] <= position[node_b]:
                return False

        for successor in self._dag.adjacency_matrix.get(node_b, []):
            if position[successor] <= position[node_a]:
                return False

        return True

    def add_to_tabu_list(
        self, tabu_list: dict, swap: tuple[Node, Node], iteration: int
    ) -> None:
        """
        Records a swap with the iteration number, so that it can be 'expired' later
        """
        tabu_list[swap] = iteration

        expired_swaps = [
            key
            for key, value in tabu_list.items()
            if iteration - value >= self._tabu_length
        ]
        for expired in expired_swaps:
            del tabu_list[expired]

    def generate_neighbors(
        self, schedule: Schedule
    ) -> list[tuple[Schedule, tuple[int, int]]]:
        """
        Generates valid neighbouring solutions, and respects the topological constraints of the DAG
        """
        neighbors = []
        n = len(schedule)

        for k in range(n - 1):
            i = (self._last_start_index + k) % (n - 1)
            j = i + 1

            node_a, node_b = schedule[i], schedule[j]
            swap = (min(node_a, node_b), max(node_a, node_b))

            if not self.is_swap_valid(node_a, node_b, schedule):
                continue

            new_schedule = schedule.copy()
            new_schedule[i], new_schedule[j] = new_schedule[j], new_schedule[i]
            neighbors.append((new_schedule, swap))

        self._last_start_index = (self._last_start_index + 1) % (n - 1)
        return neighbors

    def tabu_search(
        self, initial_schedule: Schedule, callback: IterationCallback | None = None
    ) -> Schedule:
        # initial_schedule is x_0 in the slides

        self.best_schedule = None
        self.best_tardiness = float("inf")
        tabu_list = {}  # tracks swaps with their iteration numbers

        current_schedule = initial_schedule
        current_tardiness = current_schedule.total_cost()
        g_best = current_tardiness  # best cost

        for iteration in range(self._max_iterations):
            neighbors = self.generate_neighbors(current_schedule)

            best_neighbor = None
            best_neighbor_tardiness = float("inf")
            best_swap = None

            for neighbor, swap in neighbors:
                tardiness = neighbor.total_cost()
                delta = current_tardiness - tardiness

                # if the improvement is good enough and it's not in the tabu list
                #   or if the solution is better than the global best (aspiration criteria),
                #   then accept this solution is accepted
                if delta > -self._gamma and swap not in tabu_list:
                    if tardiness < best_neighbor_tardiness:
                        best_neighbor = neighbor
                        best_neighbor_tardiness = tardiness
                        best_swap = swap

            if best_neighbor is not None:
                current_schedule = best_neighbor
                current_tardiness = best_neighbor_tardiness
                self.add_to_tabu_list(tabu_list, best_swap, iteration)

                g_best = min(g_best, current_tardiness)
                if current_tardiness < self.best_tardiness:
                    self.best_schedule = current_schedule.copy()
                    self.best_tardiness = current_tardiness

            if callback is not None:
                callback(
                    iteration,
                    [s.total_cost() for s, _ in neighbors],
                    list(tabu_list.keys()),
                    self.best_tardiness,
                    [swap != best_swap and swap in tabu_list for _, swap in neighbors],
                    best_neighbor,
                )

            if not best_neighbor:
                break

        return self.best_schedule
