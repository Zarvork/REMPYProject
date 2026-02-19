import statistics
import time

import numpy as np
from sqlmodel import Session

import backend.data.repository.benchmark_repository as benchmark_repository
from backend.converter.image_to_bytes_converter import image_to_bytes
from backend.utils.propagation import propagation
from backend.utils.propagation_fast import propagation_njit


def benchmark_function(func, image_arr, mask_arr):
    start = time.perf_counter()
    result = func(image_arr, mask_arr).astype(np.uint8)
    end = time.perf_counter()
    elapsed = end - start
    return elapsed, result


def benchmark_multiple(func, image_arr, mask_arr, n_runs=1):
    times = []
    result = None
    for _ in range(n_runs):
        elapsed, result_func = benchmark_function(func, image_arr, mask_arr)
        times.append(elapsed)
        result = result_func
    mean_time = statistics.mean(times)
    return mean_time, times, result


def create_benchmark(
    session: Session, image_arr: np.ndarray, mask_arr: np.ndarray, nb_run: int
):

    # Do the benchmark for the normal propagation
    mean_time_normal, times_normal, result_propagation = benchmark_multiple(
        propagation, image_arr, mask_arr, n_runs=nb_run
    )

    # Do the benchmark for the optimal propagation
    mean_time_opti, times_opti, result_propagation_opti = benchmark_multiple(
        propagation_njit, image_arr, mask_arr, n_runs=nb_run
    )

    # Convert image to bytes
    image_bytes = image_to_bytes(image_arr)

    # Convert mask to bytes
    mask_bytes = image_to_bytes(mask_arr)

    # Convert the normal result to bytes
    result_propagation_bytes = image_to_bytes(result_propagation)

    # Convert the opti result to bytes
    result_propagation_opti_bytes = image_to_bytes(result_propagation_opti)

    id = benchmark_repository.add_benchmark(
        session=session,
        image=image_bytes,
        mask=mask_bytes,
        result_normal=result_propagation_bytes,
        result_opti=result_propagation_opti_bytes,
        mean_time_normal=mean_time_normal,
        mean_time_opti=mean_time_opti,
        individual_times_normal=times_normal,
        individual_times_opti=times_opti,
    )

    return id


def get_image_by_id(session: Session, id: int):
    benchmark = benchmark_repository.get_benchmark_by_id(session, id)
    return benchmark.image


def get_mask_by_id(session: Session, id: int):
    benchmark = benchmark_repository.get_benchmark_by_id(session, id)
    return benchmark.mask


def get_benchmark_by_id(session: Session, id: int):
    return benchmark_repository.get_benchmark_by_id(session, id)


def get_result_normal_by_id(session: Session, id: int):
    benchmark = benchmark_repository.get_benchmark_by_id(session, id)
    return benchmark.result_normal


def get_result_opti_by_id(session: Session, id: int):
    benchmark = benchmark_repository.get_benchmark_by_id(session, id)
    return benchmark.result_opti


def get_all_benchmark_id(session: Session):
    all_benchmark = benchmark_repository.get_all_benchmark(session)
    return [benchmark.id for benchmark in all_benchmark]
