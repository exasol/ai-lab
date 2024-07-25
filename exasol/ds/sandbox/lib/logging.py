import logging
from enum import Enum

from rich.logging import RichHandler

SUPPORTED_LOG_LEVELS = {"normal": logging.WARNING, "info": logging.INFO, "debug": logging.DEBUG}


class LogType(Enum):
    SETUP = "setup"
    EXPORT = "export"
    S3_BUCKETS = "s3_buckets"
    SETUP_CI_CODEBUILD = "setup_ci_codebuild"
    AWS_ACCESS = "aws_access"
    ANSIBLE = "ansible"
    DOCKER_IMAGE = "docker_image"
    CREATE_VM = "create_vm"
    SETUP_RELEASE_BUILD = "setup_release_build"
    RELEASE_BUILD = "release_build"
    RELEASE_ACCESS = "release_access"


def get_status_logger(log_type: LogType) -> logging.Logger:
    return logging.getLogger(f"ai-lab-{log_type.value}")


def set_log_level(level: str):
    try:
        target_level = SUPPORTED_LOG_LEVELS[level]
        logging.basicConfig(level=target_level, datefmt="[%X]",
                            format="%(name)s - %(message)s",
                            handlers=[RichHandler(rich_tracebacks=True)])
        # For status logger we set at least level INFO, but allow also Debug if required by user
        for log_type in LogType:
            logger = get_status_logger(log_type)
            if target_level <= logging.INFO:
                logger.setLevel(target_level)
            else:
                logger.setLevel(logging.INFO)
    except KeyError as ex:
        raise ValueError(f"log level {level} is not supported!") from ex
