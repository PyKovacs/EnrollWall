from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.app_model import AddEnrollmentRequest, EnrollmentResponse, EnrollmentStatusEnum, RoleEnum, user_role_check
from app.database import Session, get_db
from app.db_model import Course, Enrollment, User

router = APIRouter(prefix="/enrollments")

db_depends = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[EnrollmentResponse])
async def get_all_enrollments(db: db_depends):
    return db.query(Enrollment).all()


@router.get("/status/{enrollment_status}", response_model=list[EnrollmentResponse])
async def get_enrollments_by_status(enrollment_status: EnrollmentStatusEnum, db: db_depends):
    return db.query(Enrollment).filter(Enrollment.status == enrollment_status.value).all()


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment_by_id(enrollment_id: int, db: db_depends):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(404, detail="Enrollment not found.")
    return enrollment


@router.get("/student/{student_id}", response_model=list[EnrollmentResponse])
async def get_enrollments_by_student_id(student_id: int, db: db_depends):
    user_role_check(db, student_id, RoleEnum.STUDENT)
    return db.query(Enrollment).filter(Enrollment.student_id == student_id).all()


@router.get("/student/{student_id}/{enrollment_status})", response_model=list[EnrollmentResponse])
async def get_enrollments_by_student_id_and_status(
    student_id: int, enrollment_status: EnrollmentStatusEnum, db: db_depends
):
    user_role_check(db, student_id, RoleEnum.STUDENT)
    return (
        db.query(Enrollment)
        .filter(Enrollment.student_id == student_id)
        .filter(Enrollment.status == enrollment_status.value)
        .all()
    )


@router.get("/course/{course_id}", response_model=list[EnrollmentResponse])
async def get_enrollments_by_course_id(course_id: int, db: db_depends):
    if not db.query(Course).filter(Course.id == course_id).first():
        raise HTTPException(400, detail="Course not found.")
    return db.query(Enrollment).filter(Enrollment.course_id == course_id).all()


@router.get("/tutor/{tutor_id}", response_model=list[EnrollmentResponse])
async def get_enrollments_by_tutor_id(tutor_id: int, db: db_depends):
    user_role_check(db, tutor_id, RoleEnum.TUTOR)
    return db.query(Enrollment).join(Course).filter(Course.tutor_id == tutor_id).all()


@router.post("/", status_code=201, response_model=EnrollmentResponse)
async def add_enrollment(enrollment_request: AddEnrollmentRequest, db: db_depends):
    new_enrollment = Enrollment(**enrollment_request.model_dump())
    user_role_check(db, new_enrollment.student_id, RoleEnum.STUDENT)
    if not db.query(Course).filter(Course.id == new_enrollment.course_id).first():
        raise HTTPException(400, detail="Course not found.")
    new_enrollment.enrollment_date = datetime.now()
    new_enrollment.completion_date = None
    new_enrollment.status = enrollment_request.status.value
    db.add(new_enrollment)
    db.commit()

    return new_enrollment


@router.put("/{enrollment_id}", response_model=EnrollmentResponse, status_code=200)
async def update_enrollment(enrollment_id: int, enrollment_request: AddEnrollmentRequest, db: db_depends):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(404, detail="Enrollment not found.")
    if not db.query(User).filter(User.id == enrollment_request.student_id).first():
        raise HTTPException(400, detail="Student not found.")
    if not db.query(Course).filter(Course.id == enrollment_request.course_id).first():
        raise HTTPException(400, detail="Course not found.")
    enrollment.status = enrollment_request.status
    db.commit()

    return enrollment


@router.delete("/{enrollment_id}", status_code=204)
async def delete_enrollment(enrollment_id: int, db: db_depends):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(404, detail="Enrollment not found.")

    db.delete(enrollment)
    db.commit()
    return None


@router.patch("/{enrollment_id}/complete", response_model=EnrollmentResponse)
async def complete_enrollment(enrollment_id: int, db: db_depends):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(404, detail="Enrollment not found.")
    enrollment.completion_date = datetime.now()
    enrollment.status = EnrollmentStatusEnum.COMPLETED.value
    db.commit()

    return enrollment


@router.patch("/{enrollment_id}/drop", response_model=EnrollmentResponse)
async def drop_enrollment(enrollment_id: int, db: db_depends):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(404, detail="Enrollment not found.")
    enrollment.status = EnrollmentStatusEnum.DROPPED.value
    db.commit()

    return enrollment
