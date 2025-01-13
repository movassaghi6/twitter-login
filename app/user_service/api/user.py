from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from aiokafka import AIOKafkaProducer
from ...kafka_service.kafka.producer import create_producer
from ...kafka_service.kafka.consumer import task_ready_event
from ..db.database import mongo_db
from ..core.security import get_user_dep, create_access_token, authenticate_user
from ..schemas.user import Token, UserSafe
from typing import Annotated
from datetime import timedelta
from ..core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from ..core.logger import setup_logging



# Set up logging
loggers = setup_logging()
logger = loggers["api"]

router = APIRouter()


# Login to generate access token
@router.post("/token")
async def logic_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        user = await authenticate_user(username=form_data.username, password=form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info(f"Successful login for user: {form_data.username}")
        access_token_expires= timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token= create_access_token(
            data={"sub": user.username}, expires_delta= access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    except Exception as e:
        """Explanation of exc_info=True
           The exc_info=True parameter in the logger.error method is used to
           include the full traceback information in the log message. This is
           particularly useful for debugging because it provides detailed context
           about where the error occurred."""
        logger.error(f"Error during login process: {str(e)}", exc_info=True)
        raise



@router.post("/twitter-login")
async def login_for_task_id(
    current_user: Annotated[UserSafe, Depends(get_user_dep)],
    producer: AIOKafkaProducer= Depends(create_producer)):

    try:
        task_ready_event.clear()
        logger.debug("Cleared task ready event")
        
        logger.info("Waiting for task to be ready")
        await task_ready_event.wait()
        
        logger.info("Task ready event received, retrieving task ID")
        task_id = await mongo_db.get_task_id()

        if task_id:
            logger.info(f"Successfully retrieved task ID: {task_id} for user {current_user.username}")
            return {"task_id": task_id}
        else:
            logger.error("Failed to retrieve task ID")
            raise HTTPException(status_code=500, detail="there was an error retrieving the task ID from the database.")
    except Exception as e:
        logger.error(f"Error during task ID retrieval for user {current_user.username}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="there was an error retrieving the task ID from the database.")


