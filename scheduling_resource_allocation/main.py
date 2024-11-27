from common.constants import CW_DAG_PATH, EXAMPLE_DAG_PATH
from models.DirectedAcyclicGraph import DirectedAcyclicGraph
from core.LCLWithTexCallback import LCLWithTexCallback


def generate_iterations_for_lcl_example():
    dag = DirectedAcyclicGraph.load_from_file(EXAMPLE_DAG_PATH)
    _, tex_data = LCLWithTexCallback(dag).run_lcl()

    all_data = "\n".join(tex_data)

    with open("artefacts/example_lcl_tex.text", "w") as f:
        f.write(all_data)


def generate_iterations_for_lcl_cw():
    dag = DirectedAcyclicGraph.load_from_file(CW_DAG_PATH)
    _, tex_data = LCLWithTexCallback(dag).run_lcl()

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


if __name__ == "__main__":
    generate_iterations_for_lcl_example()
    generate_iterations_for_lcl_cw()
