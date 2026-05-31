from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import llm, models  # noqa: F401 (models imported so tables register)
from .database import Base, engine
from .routers import deposits, employees, evaluation, judgment, leveling, tasks, training

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Digital Employee Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(training.router)
app.include_router(evaluation.router)
app.include_router(deposits.router)
app.include_router(tasks.router)
app.include_router(leveling.router)
app.include_router(judgment.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "llm": "live" if llm.is_live() else "mock"}
