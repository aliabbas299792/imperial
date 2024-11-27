import json

from common.common import (
    generate_random_tardy_topological_schedule,
    is_topologically_valid,
)
from common.constants import CW_DAG_PATH, EXAMPLE_DAG_PATH
from models.TardySchedule import TardySchedule
from models.DirectedAcyclicGraph import DirectedAcyclicGraph
from core.LCLWithTexCallback import LCLWithTexCallback
from core.TabuWithTexCallback import TabuWithTexCallback


def generate_iterations_for_lcl_example(dag: DirectedAcyclicGraph):
    _, tex_data = LCLWithTexCallback(dag).run_lcl()

    all_data = "\n".join(tex_data)

    with open("artefacts/example_lcl_tex.text", "w") as f:
        f.write(all_data)


def generate_iterations_for_lcl_cw(dag: DirectedAcyclicGraph):
    schedule, tex_data = LCLWithTexCallback(dag).run_lcl()

    select_iterations = [
        tex_data[0],
        tex_data[1],
        tex_data[4],
        tex_data[17],
        tex_data[-1],
    ]

    selected_data = "\n".join(select_iterations)

    with open("artefacts/cw_lcl_tex.text", "w") as f:
        f.write(selected_data)

    return schedule


def generate_iterations_tabu_iterations(
    dag: DirectedAcyclicGraph,
    schedule: TardySchedule,
    output_path: str,
    L=20,
    K=10,
    Y=10,
):
    best, iteration_data = TabuWithTexCallback(dag, L, K, Y).run_tabu(schedule)

    with open(output_path, "w") as f:
        f.write("\n".join([tex for _, tex in iteration_data]))

    return best


def generate_iterations_for_tabu_with_mandated_initial_solution(
    dag: DirectedAcyclicGraph,
):
    with open("data/2.1.initial_solution.json", "r") as f:
        initial_schedule_numbers = json.load(f)
        schedule = TardySchedule(initial_schedule_numbers, dag)

    for K in [10, 100, 1000]:
        _, iteration_data = TabuWithTexCallback(dag, 20, K, 10).run_tabu(schedule)

        previous_cost = None
        iterations_with_changes = []

        for iteration, entry in enumerate(iteration_data):
            current_cost = entry[0]
            if (
                previous_cost is None
                or current_cost != previous_cost
                or iteration == len(iteration_data) - 1
            ):
                iterations_with_changes.append(entry[1])
                previous_cost = current_cost

        with open(f"artefacts/cw_tabu_tex_K={K}.text", "w") as f:
            f.write("\n".join(iterations_with_changes))


if __name__ == "__main__":
    example_dag = DirectedAcyclicGraph.load_from_file(EXAMPLE_DAG_PATH)
    cw_dag = DirectedAcyclicGraph.load_from_file(CW_DAG_PATH)

    generate_iterations_for_lcl_example(example_dag)
    lcl_schedule = generate_iterations_for_lcl_cw(cw_dag)

    print(
        f"Optimal solution using LCL: {lcl_schedule}\n\tWith cost: {lcl_schedule.maximum_cost()}"
    )
    print("")

    generate_iterations_for_tabu_with_mandated_initial_solution(cw_dag)

    random_schedule = generate_random_tardy_topological_schedule(cw_dag)
    # sanity check, the schedule obeys the topological constraints
    assert is_topologically_valid(random_schedule, cw_dag)
    generate_iterations_tabu_iterations(
        cw_dag, random_schedule, "artefacts/cw_tabu_tex_random.text"
    )

    # initial schedule and parameters I've found to give what seems to be an optimal solution
    L = 60
    K = 500
    Y = 20  # gamma
    initial_schedule = TardySchedule(
        [
            29,
            28,
            13,
            9,
            8,
            26,
            22,
            19,
            3,
            27,
            2,
            7,
            6,
            5,
            25,
            18,
            21,
            24,
            20,
            12,
            17,
            16,
            15,
            11,
            23,
            4,
            1,
            14,
            10,
            0,
            30,
        ],
        cw_dag,
    )
    best = generate_iterations_tabu_iterations(
        cw_dag, initial_schedule, "artefacts/cw_tabu_tex_optimal.text", L, K, Y
    )

    print(
        f"Optimal solution using Tabu Search: {best}\n\tWith cost: {best.total_cost()}"
    )
