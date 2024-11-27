import json
from pathlib import Path
from pydantic import BaseModel

from models.Node import Node
from models.OperationType import OperationType


class DirectedAcyclicGraph(BaseModel):
    nodes: dict[int, Node]
    operation_processing_time: dict[OperationType, int]
    adjacency_matrix: dict[int, list[int]]
    reverse_adjacency_matrix: dict[int, list[int]]
    node_in_degrees: dict[int, int]
    node_out_degrees: dict[int, int]

    @staticmethod
    def load_from_file(file_path: Path) -> "DirectedAcyclicGraph":
        with open(file_path, "r") as f:
            data = json.load(f)
        return DirectedAcyclicGraph.model_validate(data)

    def node_processing_time(self, node_id: int) -> int:
        return self.operation_processing_time[self.nodes[node_id].operation]
