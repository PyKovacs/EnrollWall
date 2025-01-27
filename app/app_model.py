from datetime import datetime
from enum import Enum

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db_model import User


### ROLE / USERS
class RoleEnum(Enum):
    TUTOR = "tutor"
    STUDENT = "student"
    ADMIN = "admin"


class AddUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    role: RoleEnum
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    role: RoleEnum


def user_role_check(db: Session, user_id: int, role: RoleEnum):  # TODO - consider moving to separate file
    """
    Check if the user exists and has the role specified.
    Raise an HTTPException if the user does not exist or has a different role.
    """
    user_exists = db.query(User).filter(User.id == user_id).first()
    is_in_role = user_exists and user_exists.role == role.value
    if not is_in_role:
        raise HTTPException(400, detail=f"{role.value.capitalize()} not found.")


### COURSES
class EnrollmentStatusEnum(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


class AddEnrollmentRequest(BaseModel):
    course_id: int
    student_id: int
    status: EnrollmentStatusEnum


class EnrollmentResponse(BaseModel):
    id: int
    course_id: int
    student_id: int
    enrollment_date: datetime
    completion_date: datetime | None = None
    status: EnrollmentStatusEnum
