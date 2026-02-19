from fastapi import Depends, FastAPI, HTTPException, Response, UploadFile
from imageio.v3 import imread
from sqlmodel import Session

import backend.domain.benchmark_service as benchmark_service
from backend.data.repository.benchmark_repository import (
    create_db_and_tables,
    get_session,
)
from backend.presentation.benchmark_response import BenchmarkResponse

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/create_benchmark/", response_model=BenchmarkResponse)
async def create_benchmark(
    image: UploadFile, mask: UploadFile, session: Session = Depends(get_session)
):
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

    id = benchmark_service.create_benchmark(session, image_arr, mask_arr)

    return BenchmarkResponse(
        id=id,
        image_url=f"/benchmarks/{id}/image",
        mask_url=f"/benchmarks/{id}/mask",
        result_url=f"/benchmarks/{id}/result",
    )


@app.get("/benchmarks/{id}/image")
def get_image(id: int, session: Session = Depends(get_session)):
    result = benchmark_service.get_image_by_id(session, id)
    return Response(result, media_type="image/png")


@app.get("/benchmarks/{id}/mask")
def get_mask(id: int, session: Session = Depends(get_session)):
    result = benchmark_service.get_mask_by_id(session, id)
    return Response(result, media_type="image/png")


@app.get("/benchmarks/{id}/result")
def get_result(id: int, session: Session = Depends(get_session)):
    result = benchmark_service.get_result_by_id(session, id)
    return Response(result, media_type="image/png")


@app.get("/benchmarks/", response_model=list[BenchmarkResponse])
def get_all_benchmark(session: Session = Depends(get_session)):
    all_id = benchmark_service.get_all_benchmark_id(session)
    result = []
    for id in all_id:
        result.append(
            BenchmarkResponse(
                id=id,
                image_url=f"/benchmarks/{id}/image",
                mask_url=f"/benchmarks/{id}/mask",
                result_url=f"/benchmarks/{id}/result",
            )
        )
    return result
