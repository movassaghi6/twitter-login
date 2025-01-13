import logging
import sys



def setup_logging():
    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Create separate loggers for different components
    loggers = {
        "api": logging.getLogger("api"),
        "db": logging.getLogger("db"),
        "security": logging.getLogger("security"),
        "middleware": logging.getLogger("middleware")
    }

    # Ensure that loggers do not propagate to the root logger
    for logger in loggers.values():
        logger.propagate = True

    return loggers