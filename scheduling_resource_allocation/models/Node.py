from pydantic import BaseModel
from models.OperationType import OperationType


class Node(BaseModel):
    id: int
    operation: OperationType
    due_date: int
