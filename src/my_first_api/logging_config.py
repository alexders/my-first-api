"""日志配置：集中定义格式和级别，其他地方只管 getLogger。"""

import logging.config


def setup_logging(level: str = "INFO", sql_level: str = "WARNING") -> None:
    """配置根 logger 和 SQLAlchemy 的日志级别。在应用启动最早期调用一次。"""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)-7s [%(name)s] %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "loggers": {
                "sqlalchemy.engine": {
                    "level": sql_level,
                    "propagate": True,
                }
            },
            "root": {"handlers": ["console"], "level": level},
        }
    )
