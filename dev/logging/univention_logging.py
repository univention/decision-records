#
# Univention Python logging library proof of concept
#

# Example that shows that logging from:
# - our own code using the Python standard library logging module,
# - our own code using Loguru, and
# - a third party package (requests) using the Python standard library logging module,
# works consistently.
# Also shows that log levels can be transported transparently into journald.

# ### Install:
# python3 -m venv venv
# . venv/bin/activate
# pip install logfmter loguru orjson
#
# ### Example execution:
# pip install requests
# python3 -c 'import logging, requests; from univention_logging import setup_logging, logger as loguru_logger; setup_logging(); python_logger = logging.getLogger(); loguru_logger = loguru_logger.bind(x=12); python_logger.info("Info from Python."); loguru_logger.info("Info from Loguru."); python_logger.error("Error from Python."); loguru_logger.error("Error from Loguru.", y=["B"]); requests.get("https://www.univention.de")'
#
# 2024-03-12 12:26:36.850 +0100 |    INFO | 2183734 | <string>.<module> | Info from Python. |
# 2024-03-12 12:26:36.850 +0100 |    INFO | 2183734 | <string>.<module> | Info from Loguru. | x=12
# 2024-03-12 12:26:36.850 +0100 |   ERROR | 2183734 | <string>.<module> | Error from Python. |
# 2024-03-12 12:26:36.850 +0100 |   ERROR | 2183734 | <string>.<module> | Error from Loguru. | x=12 y=['B']
# 2024-03-12 12:26:36.851 +0100 |   DEBUG | 2183734 | connectionpool._new_conn | Starting new HTTPS connection (1): www.univention.de:443 |
# 2024-03-12 12:26:36.973 +0100 |   DEBUG | 2183734 | connectionpool._make_request | https://www.univention.de:443 "GET / HTTP/1.1" 200 None |
#
# ### Redirect output from same command into journald, like it'd happen from a systemd unit:
# python3 -c 'impo... ...ntion.de")' 2>&1 | systemd-cat
# journalctl --output verbose --output-fields MESSAGE,PRIORITY --no-pager -n 10

import functools
import inspect
import logging
import os.path
import sys

import logfmter
import orjson
from loguru import logger


LOG_FORMAT_SERIALIZE = "{message}"
LOG_FORMAT_NORMAL = (
    "{_syslog_prio}"
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS ZZ}</green> | "
    "<level>{level:>7}</level> | "
    "{process} | "
    "{module}.{function} | "
    "<level>{message}</level> | "
    "{extra[serialized]}"
)
_app_module_log_levels = {
    "": {"uni": "INFO"},
    "level_conf.py": {"uni.adm.hand": "DEBUG", "uni.listen": "WARNING", "uni.radius": "ERROR"},
}


def setup_logging(application: str = "", serialize: bool = False, data_format: str = "LOGFMT") -> None:
    application = _get_application_name(application)
    logger.remove()
    logger.add(
        sys.stderr,
        format=LOG_FORMAT_SERIALIZE if serialize else LOG_FORMAT_NORMAL,
        level=get_service_log_level(application),
        filter=get_module_log_levels(application),
        colorize=not serialize and sys.stderr.isatty(),
        serialize=serialize,
    )
    if not serialize:
        logger.configure(
            patcher=functools.partial(
                _patching,
                serialize=serialize,
                data_format=data_format,
                is_tty=sys.stderr.isatty()
            )
        )
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)


def get_module_log_levels(application: str = "") -> dict:
    application = _get_application_name(application)
    default_levels = _app_module_log_levels.get("", {}).copy()
    app_levels = _app_module_log_levels.get(application, {})
    default_levels.update(app_levels)
    return default_levels


def set_module_log_levels(filter_cfg: dict, application: str = "") -> None:
    application = _get_application_name(application)
    _app_module_log_levels[application] = filter_cfg


def get_service_log_level(application: str) -> str:
    if application == "level_conf.py":
        return "TRACE"
    elif application == "level_conf_warn.py":
        return "WARNING"
    return "INFO"


def _get_application_name(application: str) -> str:
    return application or os.path.basename(inspect.stack()[2].filename)


def _log_level_to_syslog_priority(level: int) -> int:
    if level < 20:    # < logging.INFO -> Priority Debug
        return 7
    elif level < 30:  # < logging.WARNING -> Priority Informational
        return 6
    elif level < 40:  # < logging.ERROR -> Priority Warning
        return 4
    elif level < 50:  # < logging.CRITICAL -> Priority Error
        return 3
    else:             # -> Priority Critical
        return 2


def _patching(record, serialize: bool, data_format: str, is_tty: bool) -> None:
    if serialize or data_format == "JSON":
        record["extra"]["serialized"] = orjson.dumps(
            record["extra"],
            default=str,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SORT_KEYS,
        ).decode()
    elif data_format == "LOGFMT":
        record["extra"]["serialized"] = logfmter.Logfmter.format_params(record["extra"])
    else:
        raise ValueError(f"Unsupported format in DATA_FORMAT:  {data_format!r}")
    record["_syslog_prio"] = "" if is_tty else f"<{_log_level_to_syslog_priority(record['level'].no)}>"


class _InterceptHandler(logging.Handler):
    """
    Copied from https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller where the logged message originated from.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
