"""
Logging module for the fritzconnection library. By default
fritzconnection will emit all messages with a log-level of INFO and
higher (WARNING, ERROR, CRITICAL).

The fritzconnection logger, defined as `fritzlogger`, is an
instance of the `logging.Logger` class from the `stdlib` and can get
accessed by:

>>> from fritzconnection.core.logger import fritzlogger

This module provides the additional functions
`activate_local_debug_mode` and `reset` (see below) to activate a debug
mode, suppressing handler-propagation, and to reset the logger to the
initial state. To activate debug logging for fritzconnection call:

>>> from fritzconnection.core.logger import activate_local_debug_mode
>>> activate_local_debug_mode(handler=logging.StreamHandler())

In this debug mode fritzconnection will additionally log the data
transfered between the library and the router and suppress
logging-propagation to the parent-handlers. Here the `StreamHandler` will
send all data to `stderr`. Because this can be a lot of data a `FileHandler`
may be a better choice:

>>> activate_local_debug_mode(handler=logging.FileHandler(<the_file>))

To deactivate this mode call `reset()`:

>>> from fritzconnection.core.logger import reset
>>> reset()

Beside this you can do everything with `fritzlogger` as with the
`logging.Logger`, because `fritzlogger` is an instance of the latter.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)


import logging


fritzlogger = logging.getLogger("fritzconnection")
fritzlogger.setLevel(logging.INFO)
fritzformatter = logging.Formatter(logging.BASIC_FORMAT)


def activate_local_debug_mode(handler=None, propagate=False):
    """
    Activates all logging messages on debug level and don't propagate to
    parent-handlers. If no handler is given the NullHandler will get
    set, avoiding a call of the lastResort-handler.
    If the given handler has no formatter, the fritzformatter gets set
    (which provides the `logging.BASIC_FORMAT`).
    If propagate is True, all debug information will also get sent to
    the parent-handlers. Keep in mind, that this can be a lot of data if
    the parent-handlers are enabled for debug-level records.
    """
    if handler is None:
        handler = logging.NullHandler()
    if not handler.formatter:
        handler.setFormatter(fritzformatter)
    fritzlogger.addHandler(handler)
    fritzlogger.propagate = propagate
    fritzlogger.setLevel(logging.DEBUG)


def reset(keep_handlers=False, propagate=True):
    """
    Resets the logger to the initial state, i.e. after calling
    `activate_local_debug_mode`. All handlers will be removed, except
    `keep_handlers` is set to True.
    """
    if not keep_handlers:
        fritzlogger.handlers = []
    fritzlogger.propagate = propagate
    fritzlogger.setLevel(logging.INFO)
