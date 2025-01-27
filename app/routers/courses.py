from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.database import Session, get_db
from app.db_model import Course, User

router = APIRouter(prefix="/courses")

db_depends = Annotated[Session, Depends(get_db)]


class CourseModel(BaseModel):
    title: str
    description: str
    duration: int
    tutor_id: int


@router.get("/")
async def get_all_courses(db: db_depends):
    return db.query(Course).all()


@router.get("/{course_id}")
async def get_course_by_id(db: db_depends, course_id: int):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(404, detail="Course not found.")
    return course


@router.post("/", status_code=201, response_model=CourseModel)
async def add_course(db: db_depends, course_request: CourseModel):
    if db.query(Course).filter(Course.title == course_request.title).first():
        raise HTTPException(400, detail="Course title already registered.")
    user_exists = db.query(User).filter(User.id == course_request.tutor_id).first()
    is_tutor = user_exists and user_exists.role == "tutor"
    if not is_tutor:
        raise HTTPException(400, detail="Tutor not found.")
    new_course = Course(**course_request.model_dump())
    db.add(new_course)
    db.commit()

    return new_course


@router.put("/{course_id}", response_model=CourseModel, status_code=200)
async def update_course(db: db_depends, course_id: int, course_request: CourseModel):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(404, detail="Course not found.")
    if db.query(Course).filter(Course.title == course_request.title).first():
        raise HTTPException(400, detail="Course title already registered.")
    user_exists = db.query(User).filter(User.id == course_request.tutor_id).first()
    is_tutor = user_exists and user_exists.role == "tutor"
    if not is_tutor:
        raise HTTPException(400, detail="Tutor not found.")

    course.title = course_request.title
    course.description = course_request.description
    course.duration = course_request.duration
    course.tutor_id = course_request.tutor_id

    db.commit()

    return course


@router.delete("/{course_id}", status_code=204)
async def delete_course(db: db_depends, course_id: int):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(404, detail="Course not found.")

    db.delete(course)
    db.commit()
    return None
