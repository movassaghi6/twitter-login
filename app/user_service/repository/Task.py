from typing import Optional
from ..models.user import Task
from ..core.logger import setup_logging

# Set up logging
loggers = setup_logging()
logger = loggers["db"]


class TaskRepo:
    """
    Data Access Object for Task model.
    Encapsulates database operations for tasks.
    """
    async def create(status: str) -> Optional[Task]:
        """
        Create a new task with the given status.
        
        Args:
            status (str): The status of the task.
        """
        try:
            task = Task(status=status)
            await task.create()
            logger.info(f"Task created with status: {status}")
        except Exception as e:
            logger.error(f"Error creating task: {e}", exc_info=True)
            return None

    async def get_by_id() -> Optional[str]:
        """
        Retrieve the ID of the most recently created task.
        
        Returns:
            Optional[str]: The task ID if found, else None.
        """
        try:
            task = await Task.find().sort("-_id").limit(1).first_or_none()
            if task:
                logger.info(f"Latest Task ID retrieved: {task.id}")
                return str(task.id)
            else:
                logger.warning("No Task found")
                return None
        except Exception as e:
            logger.error(f"Error getting latest task ID: {e}", exc_info=True)
            return None


