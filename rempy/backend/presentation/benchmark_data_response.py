from datetime import datetime

from sqlmodel import SQLModel


class BenchmarkDataResponse(SQLModel):
    mean_time_normal: float
    mean_time_opti: float
    individual_times_normal: str
    individual_times_opti: str
    created_at: datetime
