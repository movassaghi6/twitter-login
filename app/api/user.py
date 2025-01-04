from fastapi import APIRouter, Depends
from aiokafka import AIOKafkaProducer
from app.kafka import create_producer


router = APIRouter()


@router.post("/twitter-login")
async def login_for_task_id(producer: AIOKafkaProducer= Depends(create_producer)):
    return producer



