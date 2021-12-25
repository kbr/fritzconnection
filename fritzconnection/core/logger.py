"""
Logging module for the fritzconnection library. By default
fritzconnection will emit all messages with a log-level of INFO or
higher (WARNING, ERROR, CRITICAL).

The fritzconnection logger is defined as `fritzlogger` and is an
instance of the `logging.Logger` class from the stdlib and can get
accessed by:

>>> from fritzconnection.core.logger import fritzlogger

This module provides the additional functions
`activate_local_debug_mode` and `reset` (see below) to activate a debug
mode, suppressing handler-propagation, and to reset the logger to the
initial state.

In debug mode fritzconnection will log the data transfered between the
library and the router. That can be a lot of data, especially on
instanciating FritzConnection.
"""

import logging


fritzlogger = logging.getLogger("fritzconnection")
fritzlogger.setLevel(logging.INFO)


def activate_local_debug_mode(handler=None, propagate=False):
    """
    Activates all logging messages on debug level but don't propagate to
    parent-handlers. However, if no handler is set at all, messages will
    propagate to the lastResort which by default is a StreamHandler with
    level.NOTSET, therefore emitting everything to stderr.
    It can be useful to provide a file-handler because running
    fritzlogger with DEBUG level will produce a lot of output.
    """
    fritzlogger.propagate = propagate
    if handler:
        fritzlogger.addHandler(handler)
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
