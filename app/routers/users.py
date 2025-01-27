from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from app.app_model import AddUserRequest, UserResponse
from app.database import Session, get_db
from app.db_model import User

from ..dependencies import get_settings

settings = get_settings()
router = APIRouter(prefix="/users")


db_depends = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"])


@router.get("/", response_model=list[UserResponse])
async def get_all_users(db: db_depends):
    return db.query(User).all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(db: db_depends, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="User not found.")
    return user


@router.post("/", status_code=201, response_model=UserResponse)
async def add_user(db: db_depends, user_request: AddUserRequest):
    user_request.password = bcrypt_context.hash(user_request.password)
    new_user = User(**user_request.model_dump())
    new_user.role = user_request.role.value  # transform Enum to str
    try:
        db.add(new_user)
        db.commit()
    except IntegrityError:  # DB Constrain
        raise HTTPException(400, detail="Email already registered.")

    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(db: db_depends, user_id: int, user_request: AddUserRequest):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="User not found.")
    user.email = user_request.email
    user.first_name = user_request.first_name
    user.last_name = user_request.last_name
    user.role = user_request.role.value  # transform Enum to str
    user.password = bcrypt_context.hash(user_request.password)
    db.commit()

    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(db: db_depends, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="User not found.")
    db.delete(user)
    db.commit()
    return
