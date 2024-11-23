from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.database import Session, get_db
from app.db_model import Course

router = APIRouter(prefix="/courses")

db_depends = Annotated[Session, Depends(get_db)]


class AddCourseRequest(BaseModel):
    title: str
    description: str
    duration: int


@router.get("/")
async def get_all_courses(db: db_depends):
    return db.query(Course).all()


@router.post("/", status_code=201)
async def add_course(db: db_depends, course_request: AddCourseRequest):
    new_course = Course(**course_request.model_dump())
    try:
        db.add(new_course)
        db.commit()
    except IntegrityError:
        raise HTTPException(400, detail="Email already registered.")
