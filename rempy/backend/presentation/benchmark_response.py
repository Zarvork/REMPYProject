from sqlmodel import SQLModel


class BenchmarkResponse(SQLModel):
    id: int
    image_url: str
    mask_url: str
    result_url: str
