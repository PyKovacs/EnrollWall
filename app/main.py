from fastapi import FastAPI

from .database import engine
from .db_model import Base
from .routers import courses, users

Base.metadata.create_all(bind=engine)


app = FastAPI(root_path="/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


app.include_router(courses.router)
app.include_router(users.router)
