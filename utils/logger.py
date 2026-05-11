import logging
import os

LOG_FORMAT = "[%(levelname)s][%(asctime)s][%(name)s] %(message)s"
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    # В консоль — только INFO и выше
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(LOG_FORMAT))

    # В файл — всё включая DEBUG
    file_h = logging.FileHandler(
        os.path.join(LOG_DIR, "tests.log"), encoding="utf-8"
    )
    file_h.setLevel(logging.DEBUG)
    file_h.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(console)
    logger.addHandler(file_h)
    return logger