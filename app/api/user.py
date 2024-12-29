from fastapi import APIRouter
from schemas import User
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
#from settings import loop
from utils import parse_kafka_message
import json


router = APIRouter()

@router.post('/twitter-login')
async def login_for_task_id(user_credentials: User):
    # create a producer instance
    producer = AIOKafkaProducer(
        #loop=loop,
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8')) # Serialize values to JSON)
    
    await producer.start()
    try:
        # Serialize pydantic object into a dictionary
        user_data = user_credentials.model_dump()

        await producer.send_and_wait("twitter_login_requests", user_data)
        return {"status": "message sent"}
    finally:
        await producer.stop()


# kafka consumer
async def create_consumer():
    consumer = AIOKafkaConsumer(
        "twitter_login_requests",
        #loop=loop,
        bootstrap_servers="localhost:9092",
    )
    await consumer.start()
    try:
        async for msg in consumer:
            parse_kafka_message(msg)

    finally:
        await consumer.stop()
    

