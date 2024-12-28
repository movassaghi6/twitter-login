from fastapi import APIRouter
from app.schemas import User
from aiokafka import AIOKafkaProducer
import json


router = APIRouter()


@router.post('/twitter-login')
async def login_for_task_id(user_credentials: User):
    # create a producer instance
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8')) # Serialize values to JSON)
    await producer.start()
    try:
        # Serialize the Pydantic object into a dictionary
        user_data = user_credentials.model_dump_json()
        await producer.send_and_wait("twitter_login_requests", user_data)
        return {"status": "message sent"}
    finally:
        await producer.stop()
    
    