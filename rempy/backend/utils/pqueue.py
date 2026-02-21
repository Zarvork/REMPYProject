import heapq
from typing import Any


class PQueue:
    def __init__(self):
        self.heap = []
        self.current_priority = {}

    def push(self, p: float, v: Any):
        self.current_priority[v] = p
        heapq.heappush(self.heap, (p, v))

    def pop(self) -> tuple[float, Any]:
        while len(self.heap) > 0:
            p, v = heapq.heappop(self.heap)
            if self.current_priority.get(v) == p:
                del self.current_priority[v]
                return p, v
        raise Exception("pop from empty queue")

    def empty(self) -> bool:
        return len(self.current_priority) == 0
