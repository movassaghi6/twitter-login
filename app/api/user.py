from fastapi import APIRouter
from schemas import User


router = APIRouter()


@router.post(
    '/twitter-login',
)
def login_for_task_id(user_credentials: User):
    