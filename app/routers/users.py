from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.database import Session, get_db
from app.db_model import User

from ..dependencies import get_settings

settings = get_settings()
router = APIRouter(prefix="/users")

HASH_SECRET_KEY = settings.HASH_SECRET_KEY
HASH_ALGORITHM = settings.HASH_ALGORITHM

db_depends = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"])


class AddUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: str  # TODO add email validation via pydantic
    role: str
    password: str


@router.get("/")
async def get_all_users(db: db_depends):
    return db.query(User).all()


@router.post("/", status_code=201)
async def add_user(db: db_depends, user_request: AddUserRequest):
    user_request.password = bcrypt_context.hash(user_request.password)
    new_user = User(**user_request.model_dump())
    try:
        db.add(new_user)
        db.commit()
    except IntegrityError:  # DB Constrain
        raise HTTPException(400, detail="Email already registered.")
