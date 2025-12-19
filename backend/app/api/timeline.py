from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_timeline():
    # MVP: placeholder
    return {"timeline": []}
