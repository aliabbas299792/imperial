from itertools import accumulate

from common.models import DirectedAcyclicGraph


def schedule_completion_times(
    schedule: list[int], dag: DirectedAcyclicGraph
) -> list[int]:
    return list(accumulate([dag.node_processing_time(n_id) for n_id in schedule]))


def schedule_tardiness(schedule: list[int], dag: DirectedAcyclicGraph) -> list[int]:
    completion_times = schedule_completion_times(schedule, dag)
    return [
        tardiness_cost_fn(C_j, dag.nodes[n_id].due_date)
        for n_id, C_j in zip(schedule, completion_times)
    ]


def schedule_maximum_cost(schedule: list[int], dag: DirectedAcyclicGraph) -> int:
    return max(schedule_tardiness(schedule, dag))


def tardiness_cost_fn(C_j: int, d_j: int):
    return max(0, C_j - d_j)


def update_successorless_nodes(
    newly_scheduled_job: int,
    running_out_degs: dict[int, int],
    successorless_nodes: set[int],
    dag: DirectedAcyclicGraph,
):
    for parent in dag.reverse_adjacency_matrix[newly_scheduled_job]:
        running_out_degs[parent] -= 1
        if running_out_degs[parent] == 0:
            successorless_nodes.add(parent)


def select_minimising_job(
    cumulative_cost: int, successorless_nodes: set[int], dag: DirectedAcyclicGraph
):
    return min(
        successorless_nodes,
        key=lambda n_id: tardiness_cost_fn(cumulative_cost, dag.nodes[n_id].due_date),
    )


def lcl(dag: DirectedAcyclicGraph) -> list[int]:
    """
    Constructs an LCL schedule for a given DAG
    """

    running_out_degs = dag.node_out_degrees.copy()
    cumulative_cost = sum(dag.node_processing_time(n_id) for n_id in dag.nodes)
    successorless = {n for n in dag.nodes if dag.node_out_degrees[n] == 0}

    reverse_schedule = []
    while successorless:
        scheduled = None
        if len(successorless) == 1:
            scheduled = successorless.pop()
        else:
            scheduled = select_minimising_job(cumulative_cost, successorless, dag)
            successorless.remove(scheduled)

        cumulative_cost -= dag.node_processing_time(scheduled)
        reverse_schedule.append(scheduled)

        update_successorless_nodes(
            newly_scheduled_job=scheduled,
            running_out_degs=running_out_degs,
            successorless_nodes=successorless,
            dag=dag,
        )

    return reverse_schedule[::-1]
