from typing import Any


class PQueue:
    def __init__(self):
        self.heap = {}

    def push(self, p: float, v: Any):
        self.heap[v] = p

    def pop(self) -> tuple[float, Any]:
        to_delete = min(self.heap, key=lambda k: self.heap[k])
        result = (self.heap[to_delete], to_delete)
        self.heap.pop(to_delete)
        return result

    def empty(self) -> bool:
        return len(self.heap) == 0
