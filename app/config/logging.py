import logging
import logging.config
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%SZ"),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return self._to_json(log_record)

    def _to_json(self, payload: dict[str, Any]) -> str:
        parts = [f"\"{key}\": \"{str(value).replace('"', '\\"')}\"" for key, value in payload.items()]
        return "{" + ", ".join(parts) + "}"


def setup_logging(log_level: str) -> None:
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"json": {"()": JsonFormatter}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
            }
        },
        "root": {"handlers": ["console"], "level": log_level},
    }
    logging.config.dictConfig(config)
