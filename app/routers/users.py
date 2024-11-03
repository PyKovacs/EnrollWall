import os

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

HASH_SECRET_KEY = os.getenv("ENROLLWALL_HASH_SECRET_KEY")
HASH_ALGORITHM = os.getenv("ENROLLWALL_HASH_ALGORITHM")


@router.get("/")
async def get_all_users():
    return "HEY"
