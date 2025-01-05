from fastapi import APIRouter, Depends, HTTPException
from aiokafka import AIOKafkaProducer
from app.kafka import create_producer, task_ready_event
from app.database import mongo_db



router = APIRouter()


@router.post("/twitter-login")
async def login_for_task_id(producer: AIOKafkaProducer= Depends(create_producer)):
    
    task_ready_event.clear()
    
    await task_ready_event.wait()

    task_id = await mongo_db.get_task_id()

    if task_id:
        return {"task_id": task_id}
    raise HTTPException(status_code=500, detail="there was an error retrieving the task ID from the database.")



