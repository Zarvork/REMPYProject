from io import BytesIO

import numpy as np
from PIL import Image
from sqlmodel import Session

import backend.data.repository.benchmark_repository as benchmark_repository
from backend.utils.propagation import propagation


def create_benchmark(session: Session, image_arr: np.ndarray, mask_arr: np.ndarray):
    result_propagation = propagation(image_arr, mask_arr).astype(np.uint8)

    # Convert image to bytes
    image = Image.fromarray(image_arr)
    buffer_image = BytesIO()
    image.save(buffer_image, format="PNG")

    # Convert mask to bytes
    mask = Image.fromarray(mask_arr)
    buffer_mask = BytesIO()
    mask.save(buffer_mask, format="PNG")

    # Convert the result to bytes
    result_propagation_img = Image.fromarray(result_propagation)
    buffer_result_propagation_img = BytesIO()
    result_propagation_img.save(buffer_result_propagation_img, format="PNG")

    id = benchmark_repository.add_benchmark(
        session,
        buffer_image.getvalue(),
        buffer_mask.getvalue(),
        buffer_result_propagation_img.getvalue(),
    )

    return id


def get_image_by_id(session: Session, id: int):
    benchmark = benchmark_repository.get_benchmark_by_id(session, id)
    return benchmark.image


def get_mask_by_id(session: Session, id: int):
    benchmark = benchmark_repository.get_benchmark_by_id(session, id)
    return benchmark.mask


def get_result_by_id(session: Session, id: int):
    benchmark = benchmark_repository.get_benchmark_by_id(session, id)
    return benchmark.result


def get_all_benchmark_id(session: Session):
    all_benchmark = benchmark_repository.get_all_benchmark(session)
    return [benchmark.id for benchmark in all_benchmark]
