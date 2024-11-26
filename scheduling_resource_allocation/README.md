# Scheduling and Resource Allocation Coursework
This contains the coursework for COMP70068 Scheduling and Resource allocation, which involved implementing the LCL rule as well as Tabu Search.
## Usage
### Setup
Make sure you have Python 3.10, and [poetry](https://python-poetry.org/), then run `poetry install` to set up the project and its dependencies.

### Tests
Run `poetry run pytest test/lcl.py` to heuristically verify that the LCL schedule is indeed optimal.

### Data Generation
- `data/node_data_text.txt` contains the text data copied from the specification PDF
- `data/matlab_incidence_matrix.txt` contains the incidence matrix copied from the same PDF
- `data/directed_acyclic_graph.json` contains a generated DAG in JSON format

The DAG is generated using `node preprocessing/preprocessing.js`, so if you want to, you can modify those text files to alter the generated graph.

The format of the DAG is in `common/models.py`.

> The reason for this separation between the preprocessing and usage is to make it easier to switch to using a potentially different set of tools to process the DAG in the future.
