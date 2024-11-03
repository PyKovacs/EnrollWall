from fastapi import APIRouter

router = APIRouter(prefix="/courses")


@router.get("/")
async def get_all_courses():
    return "HEY"
