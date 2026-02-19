from datetime import datetime

from sqlmodel import Column, Field, LargeBinary, SQLModel


class Benchmark(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    image: bytes = Field(sa_column=Column(LargeBinary))
    mask: bytes = Field(sa_column=Column(LargeBinary))
    result_normal: bytes = Field(sa_column=Column(LargeBinary))
    result_opti: bytes = Field(sa_column=Column(LargeBinary))
    mean_time_normal: float
    mean_time_opti: float
    individual_times_normal: str
    individual_times_opti: str
    created_at: datetime = Field(default_factory=datetime.now)
