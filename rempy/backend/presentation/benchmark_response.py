from sqlmodel import SQLModel


class BenchmarkResponse(SQLModel):
    id: int
    image_url: str
    mask_url: str
    result_normal_url: str
    result_opti_url: str
    data_url: str
