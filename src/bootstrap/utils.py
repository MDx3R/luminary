import logging

from bootstrap.config import AppConfig


def log_config(logger: logging.Logger, cfg: AppConfig) -> None:
    logger.info(
        "configuration loaded",
        extra={
            "env": cfg.env,
            "config": cfg.masked_dict(),
        },
    )
