from io import BytesIO

import numpy as np
from fastapi import FastAPI, HTTPException, Response, UploadFile
from imageio.v3 import imread, imwrite
from PIL import Image

from backend.algo.propagation import propagation

app = FastAPI()


@app.post("/process/")
async def process(image: UploadFile, mask: UploadFile):
    # Read the image and mask
    image_arr = imread(image.file)
    mask_arr = imread(mask.file)

    # Verify that the image and mask have exactly the same size (necessary for algo)
    if image_arr.shape != mask_arr.shape:
        raise HTTPException(
            status_code=400, detail="Image and Mask should be the same size"
        )
    # Verify that the mask is a valid binary mask
    if not ((mask_arr == 0) | (mask_arr == 255)).all():
        raise HTTPException(
            status_code=400, detail="Mask should contain only 0 and 255 (binary values)"
        )

    result_propagation = propagation(image_arr, mask_arr).astype(np.uint8)
    result_propagation_img = Image.fromarray(result_propagation)
    buffer = BytesIO()
    result_propagation_img.save(buffer, format="PNG")
    # Save the image and mask
    imwrite("data/" + str(image.filename), image_arr)
    imwrite("data/" + str(mask.filename), mask_arr)
    imwrite("data/" + "result_" + str(image.filename), result_propagation)

    return Response(content=buffer.getvalue(), media_type="image/png")
