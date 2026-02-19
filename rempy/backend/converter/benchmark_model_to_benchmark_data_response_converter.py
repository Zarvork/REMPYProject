from backend.data.model.benchmark_model import Benchmark
from backend.presentation.benchmark_data_response import BenchmarkDataResponse


def benchmark_model_to_benchmark_data_response(benchmark: Benchmark):
    return BenchmarkDataResponse(
        mean_time_normal=benchmark.mean_time_normal,
        mean_time_opti=benchmark.mean_time_opti,
        individual_times_normal=benchmark.individual_times_normal,
        individual_times_opti=benchmark.individual_times_opti,
        created_at=benchmark.created_at,
    )
