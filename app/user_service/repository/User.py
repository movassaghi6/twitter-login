from typing import Optional
from ..models.user import User
from ..core.logger import setup_logging

# Set up logging
loggers = setup_logging()
logger = loggers["db"]


class UserRepo:
    """
    Data Access Object for User model.
    Encapsulates database operations for users.
    """
    async def get_by_username(username: str) -> Optional[User]:
        """
        Fetch a user by username.
        
        Args:
            username (str): The username to search for.
        
        Returns:
            Optional[User]: The user object if found, else None.
        """
        try:
            user = await User.find_one(User.username == username)
            if user:
                logger.info(f"User found: {username}")
            else:
                logger.warning(f"User not found: {username}")
            return user
        except Exception as e:
            logger.error(f"Error getting user by username: {e}", exc_info=True)
            return None
