import heapq
from typing import Any

import numba
import numpy as np
from numba import float64, njit
from numba.types import DictType, ListType, Tuple, UniTuple

key_type = UniTuple(numba.types.int64, 2)
value_type = numba.types.int64
tuple_type = Tuple((value_type, key_type))
heap_type = ListType(tuple_type)


@njit
def push(heap: heap_type, current_priority: dict, p: value_type, v: key_type):
    current_priority[v] = p
    heapq.heappush(heap, (p, v))


@njit
def pop(heap: heap_type, current_priority: dict) -> tuple[float, Any]:
    while len(heap) > 0:
        p, v = heapq.heappop(heap)
        if v in current_priority and current_priority[v] == p:
            del current_priority[v]
            return p, v


@njit
def propagation_njit(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    img = img.astype(np.int64)
    rows, cols = mask.shape
    D = np.full((rows, cols), 1e10)
    heap = [(np.int64(0), (np.int64(0), np.int64(0)))]
    heapq.heapify(heap)
    heapq.heappop(heap)
    current_priority = numba.typed.Dict.empty(
        key_type=key_type,
        value_type=value_type,
    )
    for l in range(rows):
        for c in range(cols):
            if mask[l, c] > 0:
                push(heap, current_priority, np.int64(0), (l, c))
                D[l, c] = 0

    while len(current_priority) > 0:
        (_, (i, j)) = pop(heap, current_priority)
        for l in range(i - 1, i + 2):
            for c in range(j - 1, j + 2):
                if l == i and c == j:
                    continue
                if l >= 0 and c >= 0 and l < D.shape[0] and c < D.shape[1]:
                    d_new = D[i, j] + abs(int(img[i, j]) - int(img[l, c]))
                    if d_new < D[l, c]:
                        D[l, c] = d_new
                        push(heap, current_priority, np.int64(d_new), (l, c))

    return D
