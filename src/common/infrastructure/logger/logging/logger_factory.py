"""Logger factory for creating application loggers."""

import logging
import sys

from common.infrastructure.config.config import RunEnvironment
from common.infrastructure.config.logger_config import LoggerConfig
from common.infrastructure.logger.logging.formatter import JSONFormatter


class LoggerFactory:
    """Factory for creating configured loggers."""

    @classmethod
    def create(
        cls, name: str | None, env: RunEnvironment, cfg: LoggerConfig
    ) -> logging.Logger:
        """Create a logger with specified configuration."""
        return cls.create_logger(name, env, cfg)

    @staticmethod
    def create_logger(
        name: str | None, env: RunEnvironment, cfg: LoggerConfig
    ) -> logging.Logger:
        """Create a logger with JSON or text formatting."""
        logger = logging.getLogger(name)
        logger.setLevel(cfg.level.value)
        logger.propagate = False

        if logger.hasHandlers():
            logger.handlers.clear()

        formatter: logging.Formatter
        if cfg.format == "json":
            formatter = JSONFormatter(pretty=(env == RunEnvironment.LOCAL))
        else:
            formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        return logger
