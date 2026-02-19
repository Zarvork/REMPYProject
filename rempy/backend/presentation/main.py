from fastapi import Depends, FastAPI, HTTPException, Response, UploadFile
from imageio.v3 import imread
from sqlmodel import Session

import backend.domain.benchmark_service as benchmark_service
from backend.converter.benchmark_model_to_benchmark_data_response_converter import (
    benchmark_model_to_benchmark_data_response,
)
from backend.converter.id_to_benchmark_response_converter import (
    id_to_benchmark_response,
    ids_to_list_benchmark_response,
)
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
    image: UploadFile,
    mask: UploadFile,
    nb_run: int | None = None,
    session: Session = Depends(get_session),
):
    # Read the image and mask
    image_arr = imread(image.file)
    mask_arr = imread(mask.file)

    # Verify that the image and mask are in PNG
    if image.content_type != "image/png" or mask.content_type != "image/png":
        raise HTTPException(
            status_code=400, detail="Image and Mask should be in the PNG format"
        )

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
    if nb_run is None:
        nb_run = 1
    id = benchmark_service.create_benchmark(session, image_arr, mask_arr, nb_run)

    return id_to_benchmark_response(id)


@app.get("/benchmarks/{id}/image")
def get_image(id: int, session: Session = Depends(get_session)):
    result = benchmark_service.get_image_by_id(session, id)
    return Response(result, media_type="image/png")


@app.get("/benchmarks/{id}/mask")
def get_mask(id: int, session: Session = Depends(get_session)):
    result = benchmark_service.get_mask_by_id(session, id)
    return Response(result, media_type="image/png")


@app.get("/benchmarks/{id}/result-normal")
def get_result_normal(id: int, session: Session = Depends(get_session)):
    result = benchmark_service.get_result_normal_by_id(session, id)
    return Response(result, media_type="image/png")


@app.get("/benchmarks/{id}/result-opti")
def get_result_opti(id: int, session: Session = Depends(get_session)):
    result = benchmark_service.get_result_opti_by_id(session, id)
    return Response(result, media_type="image/png")


@app.get("/benchmarks/", response_model=list[BenchmarkResponse])
def get_all_benchmark(session: Session = Depends(get_session)):
    all_id = benchmark_service.get_all_benchmark_id(session)
    return ids_to_list_benchmark_response(all_id)


@app.get("/benchmarks/{id}/data")
def get_benchmark_data(id: int, session: Session = Depends(get_session)):
    return benchmark_model_to_benchmark_data_response(
        benchmark_service.get_benchmark_by_id(session, id)
    )
