from io import BytesIO

import numpy as np
from PIL import Image


def image_to_bytes(image_arr: np.ndarray):
    image = Image.fromarray(image_arr)
    buffer_image = BytesIO()
    image.save(buffer_image, format="PNG")
    return buffer_image.getvalue()
