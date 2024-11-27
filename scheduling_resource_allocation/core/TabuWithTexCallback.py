from models.DirectedAcyclicGraph import DirectedAcyclicGraph
from models.Node import Node
from models.Schedule import Schedule
from models.TardySchedule import TardySchedule
from core.TabuSearchScheduler import TabuSearchScheduler


class TabuWithTexCallback:
    def __init__(
        self,
        dag: DirectedAcyclicGraph,
        tabu_length: int,
        max_iterations: int,
        gamma: int,
    ):
        self._dag = dag
        self._scheduler = TabuSearchScheduler(dag, tabu_length, max_iterations, gamma)
        self._iteration_data = []

    def _tabu_callback(
        self,
        iteration: int,
        total_costs: list[int],
        tabu_list: list[tuple[int, int]],
        best_cost: int,
        was_tabu_list_used: list[bool],
        best_neighbour: Schedule | None,
    ):
        tabu_list_str = ", ".join([f"({i}, {j})" for i, j in tabu_list])

        best_neighbour_str = (
            f"[{', '.join(map(str, best_neighbour))}]" if best_neighbour else "None"
        )

        self._iteration_data.append(
            f"""
      \\item[{iteration}.] \\textbf{{Candidate schedule costs}}: {total_costs} \\\\
      \\textbf{{Tabu list}}: \\{{ {tabu_list_str} \\}} \\\\
      \\textbf{{Best cost so far}}: {best_cost} \\\\
      \\textbf{{Tabu list used?}}: {'Yes' if any(was_tabu_list_used) else 'No'} \\\\
      \\textbf{{Selected neighbour}}: {best_neighbour_str} \\\\
      \\textbf{{Selected neighbour cost}}: {best_neighbour.total_cost() if best_neighbour else 'None'}
        """
        )

    def run_tabu(
        self, initial_schedule_numeric: list[int]
    ) -> tuple[Schedule, list[str]]:
        self._iteration_data = []
        schedule = TardySchedule(initial_schedule_numeric, self._dag)
        return self._scheduler.tabu_search(
            schedule, self._tabu_callback
        ), self._iteration_data
