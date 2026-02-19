import numba
import numpy as np
from numba import float64, njit
from numba.types import UniTuple

key_type = UniTuple(numba.types.int64, 2)
value_type = float64


@njit
def push(h: dict, p: value_type, v: key_type):
    h[v] = p


@njit
def pop(h: dict) -> key_type:
    min_key = sorted([(val, key) for key, val in h.items()])[0][1]
    result = (h[min_key], min_key)
    h.pop(min_key)
    return result


@njit
def empty(h: dict) -> bool:
    return len(h) == 0


@njit
def propagation_njit(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    img = img.astype(np.int64)
    D = np.full(mask.shape, 1e10)
    q = numba.typed.Dict.empty(
        key_type=key_type,
        value_type=value_type,
    )

    for l in range(mask.shape[0]):
        for c in range(mask.shape[1]):
            if mask[l, c] > 0:
                push(q, 0, (l, c))
                D[l, c] = 0

    while not empty(q):
        (_, (i, j)) = pop(q)
        for l in range(i - 1, i + 2):
            for c in range(j - 1, j + 2):
                if l == i and c == j:
                    continue
                if l >= 0 and c >= 0 and l < D.shape[0] and c < D.shape[1]:
                    d_new = D[i, j] + abs(int(img[i, j]) - int(img[l, c]))
                    if d_new < D[l, c]:
                        D[l, c] = d_new
                        push(q, d_new, (l, c))

    return D
