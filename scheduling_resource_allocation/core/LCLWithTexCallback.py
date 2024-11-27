from common.constants import CW_DAG_PATH
from common.models import DirectedAcyclicGraph
from common.common import tardiness_cost_fn
from core.LowestCostLassScheduler import LowestCostLastScheduler


class LCLWithTexCallback:
    def __init__(self, dag: DirectedAcyclicGraph):
        self._dag = dag
        self._scheduler = LowestCostLastScheduler(dag)
        self._iteration_data = []
        self._iteration_num = 0

    def _job_costs_str(self, available_jobs, cumulative_cost):
        def job_str(n_id):
            node = self._dag.nodes[n_id]
            cost = tardiness_cost_fn(cumulative_cost, node)
            return f"f_{{{n_id}}}(p(N)) = \\max(0, {cumulative_cost} - {node.due_date}) = {cost}"

        return ", \\quad ".join([job_str(n_id) for n_id in available_jobs])

    def _lcl_callback(
        self,
        available_jobs,
        cumulative_cost,
        new_cumulative_cost,
        scheduled_job_id,
        partial_schedule,
    ):
        v = ", ".join([str(j) for j in available_jobs])
        pN = cumulative_cost
        costs = self._job_costs_str(available_jobs, cumulative_cost)
        selected = scheduled_job_id
        new_schedule = partial_schedule

        self._iteration_data.append(
            f"""
      \\item[{self._iteration_num}.] Available jobs: $V = \\{{ {v} \\}}$ (no successors) \\\\
      $p(N) = {pN}$
      \\[
      {costs}
      \\]    
      Select $J_{{{selected}}}$ (minimises $f_j(p(N))$)

      Partial schedule cost: {partial_schedule.maximum_cost(new_cumulative_cost)}

      Updated schedule: ${new_schedule}$
        """
        )

        self._iteration_num += 1

    def run_lcl(self) -> tuple[list[int], list[str]]:
        self._iteration_data = []
        self._iteration_num = 0
        return self._scheduler.lcl(self._lcl_callback), self._iteration_data
