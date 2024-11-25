from pathlib import Path
from pydantic import BaseModel
from enum import Enum
import json

class OperationType(Enum):
    ONNX = "onnx"
    MUSE = "muse"
    EMBOSS = "emboss"
    BLUR = "blur"
    WAVE = "wave"
    VII = "vii"
    NIGHT = "night"

class Node(BaseModel):
    id: int
    operation: OperationType
    due_date: int

class DirectedAcyclicGraph(BaseModel):
    nodes: list[Node]
    operation_processing_time: dict[OperationType, int]
    adjacency_graph: dict[int, list[int]]
    
    @staticmethod
    def load_from_file(file_path: Path) -> 'DirectedAcyclicGraph':
        with open(file_path, "r") as f:
            data = json.load(f)
        return DirectedAcyclicGraph.model_validate(data)

