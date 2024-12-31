from fastapi import APIRouter, HTTPException
from schemas import User
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
#from settings import loop
from database import mongo_db
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
            try:
                # get username from consumer's message
                user = parse_kafka_message(msg).username

                if mongo_db.client is None:
                    raise Exception("MongoDB client is not initialized.")
            
                # user from database 
                user_in_db = await mongo_db.get_user_by_username(user)

                if not user_in_db:
                    print(f"User {user} not found in database.")
                else:
                    print(f"User {user} successfully fetched from database.")
            except Exception as e:
                print(f"Error processing message: {e}")
    finally:
        await consumer.stop()
    

