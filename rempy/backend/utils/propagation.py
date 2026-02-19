import numpy as np

from backend.utils.pqueue import PQueue


def propagation(img: np.ndarray, mask: np.ndarray) -> np.ndarray:
    D = np.full(mask.shape, 1e10)
    D[mask > 0] = 0
    q = PQueue()

    for l in range(mask.shape[0]):
        for c in range(mask.shape[1]):
            if mask[l, c] > 0:
                q.push(0, (l, c))

    while not q.empty():
        (_, (i, j)) = q.pop()
        n = [
            (i - 1, j),
            (i + 1, j),
            (i, j - 1),
            (i, j + 1),
            (i - 1, j - 1),
            (i - 1, j + 1),
            (i + 1, j - 1),
            (i + 1, j + 1),
        ]
        for l, c in n:
            if l >= 0 and c >= 0 and l < D.shape[0] and c < D.shape[1]:
                d_new = D[i, j] + abs(int(img[i, j]) - int(img[l, c]))
                if d_new < D[l, c]:
                    D[l, c] = d_new
                    q.push(d_new, (l, c))
    return D
