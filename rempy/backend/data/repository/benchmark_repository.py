from sqlmodel import Session, SQLModel, create_engine, select

from backend.data.model.benchmark_model import Benchmark

DATABASE_URL = "postgresql://postgres:example@localhost/postgres"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def add_benchmark(session: Session, image: bytes, mask: bytes, result: bytes):
    benchmark = Benchmark(image=image, mask=mask, result=result)
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
