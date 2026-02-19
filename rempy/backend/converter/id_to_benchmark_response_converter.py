from backend.presentation.benchmark_response import BenchmarkResponse


def id_to_benchmark_response(id: int):
    return BenchmarkResponse(
        id=id,
        image_url=f"/benchmarks/{id}/image",
        mask_url=f"/benchmarks/{id}/mask",
        result_normal_url=f"/benchmarks/{id}/result-normal",
        result_opti_url=f"/benchmarks/{id}/result-opti",
        data_url=f"/benchmarks/{id}/data",
    )


def ids_to_list_benchmark_response(ids: list[int]):
    result = []
    for id in ids:
        result.append(id_to_benchmark_response(id))
    return result
