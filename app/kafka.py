from fastapi import HTTPException
from app.schemas import User
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.database import mongo_db
from app.utils import parse_kafka_message
import json
import asyncio
from app.security import verify_password



# Temporary store for task IDs
#task_id_store={}
# An event which will be set, when task is ready
task_ready_event = asyncio.Event()


# Kafka Prodcuer
async def create_producer(user_credentials: User):
    
    # create a producer instance
    producer = AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8')) # Serialize values to JSON)
    
    await producer.start()
    try:
        # Serialize pydantic object into a dictionary
        user_data = user_credentials.model_dump()
        ##username = user_data.get("username")

        await producer.send_and_wait("twitter_login_requests", user_data)

    finally:
        await producer.stop()



# Kafka Consumer
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
                parsed_message= parse_kafka_message(msg)
                user = parsed_message.username


                if mongo_db.client is None:
                    raise Exception("MongoDB client is not initialized.")
            
                # user from database 
                user_in_db = await mongo_db.get_user_by_username(user)

                # Check input credentials for login
                if (
                    user_in_db 
                    and verify_password(parsed_message.password, user_in_db.hashed_password) 
                    and user_in_db.phone_number == parsed_message.phone_number 
                    and user_in_db.email == parsed_message.email
                ):
                    task_id = await mongo_db.create_task(status="success")
                else:
                    task_id = await mongo_db.create_task(status="failure")

                # Store task_id using a key from the kafka message
                #task_id_store[user] = task_id

                # Set the event to signal that the task is ready
                task_ready_event.set()

            except Exception as e:
                print(f"Error processing message: {e}")
    finally:
        await consumer.stop()
    
