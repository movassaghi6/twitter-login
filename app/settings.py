import os
from pathlib import Path
from starlette.config import Config
#import asyncio


ROOT_PATH = Path(__file__).parent.parent
env_file = os.environ.get("ENV_FILE") if "ENV_FILE" in os.environ else os.path.join(ROOT_PATH, ".env")

config = Config(env_file)

# env variables
#loop = asyncio.get_event_loop()

# MongoDB database
DATABASE_HOST: str = config("DATABASE_HOST")
DATABASE_NAME: str = config("DATABASE_NAME")

# Security
SECRET_KEY= config("SECRET_KEY")
ALGORITHM= config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES= config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)
