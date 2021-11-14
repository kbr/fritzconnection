import io
import logging
import pytest
from ..core.logger import fritzlogger, FritzLogger

stream = io.StringIO()
stream_handler = logging.StreamHandler(stream=stream)
formatter = logging.Formatter("%(levelname)s:%(message)s")
stream_handler.setFormatter(formatter)
message_formatter = logging.Formatter("%(message)s")
test_logger = logging.getLogger("test_logger")
test_logger.addHandler(stream_handler)


def get_last_log_entry():
    lines = stream_handler.stream.getvalue().splitlines()
    if lines:
        return lines[-1]
    return ''


def delete_log_entries():
    stream_handler.stream.close()
    stream_handler.stream = io.StringIO()


def test_add_handlers_once():
    """
    internal test that a handler-instance will not get duplicated in the
    logger handler-list.
    """
    fritzlogger.add_handler(stream_handler)
    assert len(fritzlogger.logger.handlers) == 2  # because of NullHandler
    fritzlogger.add_handler(stream_handler)
    assert len(fritzlogger.logger.handlers) == 2  # should not change


def test_remove_handler():
    """
    Remove a given handler.
    """
    fritzlogger.add_handler(stream_handler)
    num = len(fritzlogger.logger.handlers)
    fritzlogger.remove_handler(stream_handler)
    assert len(fritzlogger.logger.handlers) == num - 1
    # remove again should not raise an error
    fritzlogger.remove_handler(stream_handler)


def test_singleton():
    """
    The instance of FritzLogger should be a singleton.
    """
    second_logger = FritzLogger()
    assert second_logger is fritzlogger


def test_log_message_with_handler():
    """
    With no parent but a handler given, there should be logging.
    """
    fritzlogger.enable()  # activate first
    fritzlogger.add_handler(stream_handler)
    fritzlogger.log("message", logging.WARNING)
    result = get_last_log_entry()
    assert "WARNING:message" == result


def test_disable_enable_logger():
    """
    disable and enable the logger.
    """
    fritzlogger.add_handler(stream_handler)
    delete_log_entries()
    fritzlogger.disable()
    fritzlogger.log("disabled", logging.INFO)
    result = get_last_log_entry()
    assert "" == result
    fritzlogger.enable()
    fritzlogger.log("enabled", logging.INFO)
    result = get_last_log_entry()
    assert "INFO:enabled" == result


@pytest.mark.parametrize(
    "message, level", [
        ("const", logging.INFO),
        ("string", "info"),
        ("upper", "INFO"),
        ("mixed", "Info"),
    ])
def test_log_level_parameter_types(message, level):
    """
    Test parameters for level: const and strings.
    """
    _formatter = stream_handler.formatter
    stream_handler.setFormatter(message_formatter)
    fritzlogger.add_handler(stream_handler)
    delete_log_entries()
    fritzlogger.log(message, level)
    result = get_last_log_entry()
    stream_handler.setFormatter(_formatter)
    assert message == result


@pytest.mark.parametrize(
    "message, level, logger_level, handler_level, expected_result", [
        ("debug", "debug", logging.DEBUG, logging.DEBUG, "DEBUG:debug"),
        ("debug", "debug", logging.DEBUG, logging.WARNING, ""),
        ("debug", "debug", logging.WARNING, logging.WARNING, ""),
        ("debug", "debug", logging.WARNING, logging.DEBUG, ""),
    ])
def test_logger_handler_levels(message, level, logger_level, handler_level, expected_result):
    """
    Tests combinations logger- and handler-levels for the logger.
    """
    delete_log_entries()
    stream_handler.setLevel(handler_level)
    fritzlogger.set_level(logger_level)
    fritzlogger.add_handler(stream_handler)
    fritzlogger.log(message, level)
    result = get_last_log_entry()
    assert expected_result == result



def test_log_with_parent():
    """
    Removes handler and log with parent handler.
    """
    # first check for normal behaviour
    delete_log_entries()
    fritzlogger.add_handler(stream_handler)
    fritzlogger.log("message", "warning")
    result = get_last_log_entry()
    assert "WARNING:message" == result
    # delete the handler: no logging
    delete_log_entries()
    fritzlogger.remove_handler(stream_handler)
    fritzlogger.log("message", "warning")
    result = get_last_log_entry()
    assert "" == result
    # use the test-logger:
    delete_log_entries()
    test_logger.warning("message")
    result = get_last_log_entry()
    assert "WARNING:message" == result
    # now install test_logger as parent in fritzlogger
    delete_log_entries()
    fritzlogger.set_parent(test_logger)
    fritzlogger.log("message", "warning")
    result = get_last_log_entry()
    assert "WARNING:message" == result
    # reset parent. No log output again
    delete_log_entries()
    fritzlogger.delete_parent()
    fritzlogger.log("message", "warning")
    result = get_last_log_entry()
    assert "" == result
    # reinstall handler: logging again
    delete_log_entries()
    fritzlogger.add_handler(stream_handler)
    fritzlogger.log("message", "warning")
    result = get_last_log_entry()
    assert "WARNING:message" == result


@pytest.mark.parametrize(
    "message, level, logger_level, handler_level, expected_result", [
        ("debug", "debug", logging.DEBUG, logging.DEBUG, "DEBUG:debug"),
        ("info", "info", logging.DEBUG, logging.DEBUG, "INFO:info"),
        ("warning", "warning", logging.DEBUG, logging.DEBUG, "WARNING:warning"),
        ("error", "error", logging.DEBUG, logging.DEBUG, "ERROR:error"),
        ("critical", "critical", logging.DEBUG, logging.DEBUG, "CRITICAL:critical"),
        ("debug", "debug", logging.WARNING, logging.DEBUG, ""),
        ("info", "info", logging.WARNING, logging.DEBUG, ""),
        ("warning", "warning", logging.WARNING, logging.DEBUG, "WARNING:warning"),
        ("error", "error", logging.WARNING, logging.DEBUG, "ERROR:error"),
        ("error", "error", logging.WARNING, logging.CRITICAL, ""),
        ("critical", "critical", logging.WARNING, logging.DEBUG, "CRITICAL:critical")
    ])
def test_with_parent_log_level(
        message, level, logger_level, handler_level, expected_result):
    """
    Tests various combinations of different log-level.
    For logging at first the log-level of the called logger filters the
    log-messages. Then all handlers are invoked with their own
    log-levels, including handlers from parent-loggers. The log-levels
    of the parent loggers are ignored.
    """
    delete_log_entries()
    test_logger.setLevel(logging.CRITICAL)
    stream_handler.setLevel(handler_level)
    fritzlogger.set_level(logger_level)
    fritzlogger.remove_handler(stream_handler)
    fritzlogger.set_parent(test_logger)
    fritzlogger.log(message, level)
    result = get_last_log_entry()
    assert expected_result == result
    fritzlogger.delete_parent()
