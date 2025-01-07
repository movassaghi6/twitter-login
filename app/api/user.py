from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from aiokafka import AIOKafkaProducer
from app.kafka import create_producer, task_ready_event
from app.database import mongo_db
from app.security import get_user_dep, create_access_token, authenticate_user
from app.schemas import Token, UserSafe
from typing import Annotated
from datetime import timedelta
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES




router = APIRouter()


# Login to generate access token
@router.post("/token")
async def logic_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires= timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token= create_access_token(
        data={"sub": user.username}, expires_delta= access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")



@router.post("/twitter-login")
async def login_for_task_id(
    current_user: Annotated[UserSafe, Depends(get_user_dep)],
    producer: AIOKafkaProducer= Depends(create_producer)):
    
    task_ready_event.clear()
    
    await task_ready_event.wait()

    task_id = await mongo_db.get_task_id()

    if task_id:
        return {"task_id": task_id}
    raise HTTPException(status_code=500, detail="there was an error retrieving the task ID from the database.")



