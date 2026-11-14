import logging

NOISY_LOGGERS = (
    "discord",
    "twitchio",
    "httpx",
    "httpcore",
    "sqlalchemy.engine",
    "uvicorn.access",
)


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )

    for name in NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
