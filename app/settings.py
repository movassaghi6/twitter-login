import os
from pathlib import Path
from starlette.config import Config

ROOT_PATH = Path(__file__).parent.parent.parent
env_file = os.environ.get("ENV_FILE") if "ENV_FILE" in os.environ else os.path.join(ROOT_PATH, ".env")

config = Config(env_file)

# MongoDB database
DATABASE_HOST: str = config("DATABASE_HOST")
DATABASE_NAME: str = config("DATABASE_NAME")
