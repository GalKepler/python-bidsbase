import logging
from typing import Union
from pathlib import Path
import datetime


def initiate_logger(
    destination: Union[str, Path],
    name: str = "logger",
):
    """
    Initiate a logger

    Parameters
    ----------
    name : str, optional
        The name of the logger, by default "logger"

    Returns
    -------
    logging.Logger
        The logger
    """
    log_filename = datetime.datetime.now().strftime(
        f"{name}_%Y-%m-%d_%H-%M-%S.txt"
    )
    log_path = Path(destination) / log_filename
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.info(f"Log file created at {log_path}")
    return logger
