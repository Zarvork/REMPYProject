import json

from sqlmodel import Session, SQLModel, create_engine, select

from backend.data.model.benchmark_model import Benchmark

# db is when in container, otherwise it is localhost
DATABASE_URL = "postgresql://postgres:a_very_secure_password@localhost/postgres"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def add_benchmark(
    session: Session,
    image: bytes,
    mask: bytes,
    result_normal: bytes,
    result_opti: bytes,
    mean_time_normal: float,
    mean_time_opti: float,
    individual_times_normal: list[float],
    individual_times_opti: list[float],
):
    individual_times_normal_str = json.dumps(individual_times_normal)
    individual_times_opti_str = json.dumps(individual_times_opti)
    benchmark = Benchmark(
        image=image,
        mask=mask,
        result_normal=result_normal,
        result_opti=result_opti,
        mean_time_normal=mean_time_normal,
        mean_time_opti=mean_time_opti,
        individual_times_normal=individual_times_normal_str,
        individual_times_opti=individual_times_opti_str,
    )
    session.add(benchmark)
    session.commit()
    session.refresh(benchmark)
    return benchmark.id


def get_benchmark_by_id(session: Session, id: int):
    statement = select(Benchmark).where(Benchmark.id == id)
    benchmark = session.exec(statement).first()
    return benchmark


def get_all_benchmark(session: Session):
    all_benchmark = session.exec(select(Benchmark)).all()
    return all_benchmark
