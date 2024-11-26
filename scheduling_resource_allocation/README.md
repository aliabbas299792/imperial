# Scheduling and Resource Allocation Coursework
This contains the coursework for COMP70068 Scheduling and Resource allocation, which involved implementing the LCL rule as well as Tabu Search.
## Usage
### Setup
Make sure you have Python 3.10, and [poetry](https://python-poetry.org/), then run `poetry install` to set up the project and its dependencies.

### Tests
Run `poetry run pytest test/lcl.py` to heuristically verify that the LCL schedule is indeed optimal.

### Data Generation
- The `data/` directory contains the data describing DAGs and their incidence matrices
- `artefacts/` contains any output, including the DAG JSON files

The data was mostly copied from the PDF, but I switched it to 0-based indexing for consistency.

`1.1.example_node_data.txt` and `node_data.txt` both follow the format in the coursework specification, as do the incidence matricies `matlab_incidence_matrix.txt` and `1.1.example_incidence_matrix.txt`.

Run this to generate the DAG JSON for this coursework:
```sh
node preprocessing/preprocessing.js data/node_data.txt data/matlab_incidence_matrix.txt artefacts/cw_dag.json
```

And this to generate the DAG used in the example in the answer to question 1:
```sh
node preprocessing/preprocessing.js data/1.1.example_node_data.txt data/1.1.example_incidence_matrix.txt artefacts/
example_dag.json
```

The DAG JSON is generated using `node preprocessing/preprocessing.js`, so if you want to, you can modify those text files to alter the generated graph.

The format of the DAG is in `common/models.py`.

> The reason for this separation between the preprocessing and usage is to make it easier to switch to using a potentially different set of tools to process the DAG in the future.
### Reproducing Iteration Data
To reproduce the iteration data for question 1 in the answers PDF, run:
```sh
poetry run python main.py
```
