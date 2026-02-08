import logging
import sys

def configure_logging(logger_name: str = 'uvicorn', level: int = logging.INFO):
    """
    Configures logging for a given logger name.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Prevent adding multiple handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(levelname)s:     %(asctime)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # For Dapr SDK logging (optional)
    dapr_logger = logging.getLogger('dapr')
    dapr_logger.setLevel(level)
    if not dapr_logger.handlers:
        dapr_handler = logging.StreamHandler(sys.stdout)
        dapr_handler.setFormatter(formatter)
        dapr_logger.addHandler(dapr_handler)

    logging.info(f"Logging configured for '{logger_name}' at level {logging.getLevelName(level)}")