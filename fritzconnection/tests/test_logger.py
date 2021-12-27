import io
import logging
import pytest
from ..core.logger import (
    fritzlogger,
    activate_local_debug_mode,
    reset,
)

stream = io.StringIO()
stream_handler = logging.StreamHandler(stream=stream)
formatter = logging.Formatter("%(levelname)s:%(message)s")
stream_handler.setFormatter(formatter)


def get_last_log_entry():
    lines = stream_handler.stream.getvalue().splitlines()
    if lines:
        return lines[-1]
    return ''


def expected_log_entry(message):
    # helper function for formatting
    return f"{message.upper()}:{message}"


def delete_log_entries():
    stream_handler.stream.close()
    stream_handler.stream = io.StringIO()


@pytest.mark.parametrize(
    "message, log_call, should_log", [
        ("debug", fritzlogger.debug, False),
        ("info", fritzlogger.info, True),
        ("warning", fritzlogger.warning, True),
        ("error", fritzlogger.error, True),
        ("critical", fritzlogger.critical, True),
    ])
def test_default_logging(message, log_call, should_log):
    fritzlogger.addHandler(stream_handler)
    delete_log_entries()
    log_call(message)
    last_message = get_last_log_entry()
    if should_log:
        expected = expected_log_entry(message)
    else:
        expected = ""
    assert last_message == expected


def test_local_debug_mode_no_propagate_no_handler():
    delete_log_entries()
    reset()
    activate_local_debug_mode()
    message = "debug"
    fritzlogger.debug(message)
    # no handler (NullHandler), no propagate:
    assert get_last_log_entry() == ""


def test_local_debug_mode_no_propagate_with_handler():
    delete_log_entries()
    reset()
    activate_local_debug_mode(handler=stream_handler)
    message = "debug"
    fritzlogger.debug(message)
    assert get_last_log_entry() == expected_log_entry(message)


def test_local_debug_mode_no_handler():
    delete_log_entries()
    reset()
    activate_local_debug_mode(propagate=True)
    message = "debug"
    fritzlogger.debug(message)
    # no handler, but propagate:
    assert get_last_log_entry() == ""


def test_local_debug_mode_no_handler_but_propagate_and_warning():
    # if emitted as warning, the message gets logged from the
    # parent-handlers (in this case root)
    # in this case the RootLogger needs a handler
    delete_log_entries()
    reset()
    activate_local_debug_mode(propagate=True)
    message = "warning"
    fritzlogger.warning(message)
    assert get_last_log_entry() == ""
    # provide a handler for root:
    logging.root.addHandler(stream_handler)
    fritzlogger.warning(message)
    assert get_last_log_entry() == expected_log_entry(message)
    logging.root.removeHandler(stream_handler)
