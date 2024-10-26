from logging import Formatter, LogRecord
from typing import override
import datetime as dt
import json

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}
# 经过测试, 转换为set的速度甚至更慢, 写入50万条到本地
LOG_RECORD_BUILTIN_ATTRS = set(LOG_RECORD_BUILTIN_ATTRS)


class JsonFormatter(Formatter):
    def __init__(self, fmt_keys: list[str]):
        super().__init__()
        self.tz = dt.timezone(dt.timedelta(hours=8)) # beijing time offset relative to standard time
        self.fmt_keys = fmt_keys
    
    @override
    def format(self, record: LogRecord) -> str:
        always_fields = {
            "isotime": dt.datetime.fromtimestamp(record.created, tz=self.tz).isoformat(),
            "message": record.getMessage()
        }

        if record.exc_info:
            always_fields['exc_info'] = self.formatException(record.exc_info)

        if record.stack_info:
            always_fields['stack_info'] = self.formatStack(record.stack_info)
        
        message = {
            key: msg
            if (msg := always_fields.pop(key, None)) is not None
            else getattr(record, key)
            for key in self.fmt_keys
        }
        message.update(always_fields)
        for key,val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return json.dumps(message)