import json
from ...user_service.schemas.user import User


def parse_kafka_message(message: str) -> User:
    """
    Extracts and validates user credentials from a Kafka message.
    """
    try:
        if not message.value:
            raise ValueError("Record value is empty or None")
        
        # Parse JSON directly
        parsed_value = json.loads(message.value)

        if not isinstance(parsed_value, dict):
            raise ValueError("Parsed Kafka message is not a valid JSON object")

        return User(**parsed_value)
    
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Failed to parse Kafka message: {e}")
