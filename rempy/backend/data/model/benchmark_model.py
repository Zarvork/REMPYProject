from sqlmodel import Column, Field, LargeBinary, SQLModel


class Benchmark(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    image: bytes = Field(sa_column=Column(LargeBinary))
    mask: bytes = Field(sa_column=Column(LargeBinary))
    result: bytes = Field(sa_column=Column(LargeBinary))
