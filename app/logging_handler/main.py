import logging
from logging import FileHandler, Logger, Formatter, StreamHandler
from pathlib import Path
import sys
from typing import Tuple

from settings.config import settings


def configure_logging(
    path_data_logging: Path,
    path_errors_logging: Path,
    format_file: str,
    date_format: str,
    level=logging.INFO,
) -> Tuple[logging.Logger, logging.Logger]:
    """Конфигурация базового логгера."""

    # Если папка для логгирования не была создана, то создаем ее
    path_data_logging.parent.mkdir(parents=True, exist_ok=True)
    path_errors_logging.parent.mkdir(parents=True, exist_ok=True)

    file_handler: FileHandler = FileHandler(
        filename=str(path_data_logging), encoding="utf-8"
    )
    error_handler: FileHandler = FileHandler(
        filename=str(path_errors_logging), encoding="utf-8"
    )
    stream_handler: StreamHandler = StreamHandler(stream=sys.stdout)

    fmt: Formatter = Formatter(fmt=format_file, datefmt=date_format)
    for handler in [file_handler, error_handler, stream_handler]:
        handler.setFormatter(fmt)

    root_logging: logging.Logger = logging.getLogger(name="main_logger")

    if not root_logging.handlers:
        root_logging.setLevel(level=logging.INFO)
        root_logging.addHandler(file_handler)
        root_logging.addHandler(stream_handler)

    error_logging: logging.Logger = logging.getLogger(name="error_logger")
    if not error_logging.handlers:
        error_logging.setLevel(level=logging.ERROR)
        error_logging.addHandler(error_handler)
        error_logging.addHandler(stream_handler)

    return root_logging, error_logging


rout_logging, error_logging = configure_logging(
    path_errors_logging=settings.logging.PATH_ERRORS_LOGGING,
    path_data_logging=settings.logging.PATH_DATA_LOGGING,
    format_file=settings.logging.FORMAT_FILE,
    date_format=settings.logging.DATE_FORMAT,
)
