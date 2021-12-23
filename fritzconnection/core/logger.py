"""
Logging interface for the fritzconnection library. The interface is
considered as internal and can get used to inspect the traffic and
protocol-data exchanged with the router.

If logging is enabled, fritzconnection will log the data of all requests
and responses at debug level. This can produce a lot of output, especial
on initializing a FritzConnection-instance. To suppress output the
methods disable and enable can get called. Default mode is disabled.

On module level an instance of `FritzLogger` gets created as `fritzlogger`
that can get imported by:

>>> from fritzconnection.core.logger import fritzlogger

The fritzlogger instance is preset to logging.NOTSET. To do some logging, the logger must get enabled and a handler should be provided:

>>> fritzlogger.enable()
>>> fritzlogger.add_handler(the_handler)
>>> fritzlogger.log("the message")  # will get logged now

For convenience fritzlogger provides the methods `set_streamhandler` and
`set_filehandler` to add predefined handlers.
"""

import logging


class FritzLogger:
    """
    Wrapper for the logging library to reduce executable code on module
    global level. As multiple instances would use the same logger, to not
    get confused this class is a singleton.
    Initially the logger has no log-level, is disabled and does not propagate messages to parent handlers.
    Primary use of the logger is to report the data exchanged by the library and the router.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Be a singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Creates the internal logger instance in disabled mode."""
        self.logger = logging.getLogger("fritzconnection")
        self.disable()

    def disable(self):
        """Disables and reset the logger."""
        self.logger.disabled = True
        self.logger.propagate = False
        self.logger.setLevel(logging.NOTSET)

    def enable(self, level=logging.DEBUG, propagate=False):
        """
        Enables the logger with the given threshold level and propagate
        setting.
        """
        self.logger.setLevel(level)
        self.logger.propagate = propagate
        self.logger.disabled = False

    def set_streamhandler(self):
        """Sets the StreamHandler logging to stderr."""
        self.add_handler(logging.StreamHandler())

    def set_filehandler(self, filename):
        """Sets the FileHandler logging to the given filename."""
        self.add_handler(logging.FileHandler(filename, encoding="utf-8"))

    def add_handler(self, handler):
        """
        Add a handler to the logger.

        Handlers will just added once, even if this method get called
        multiple times with the same handler.
        """
        self.logger.addHandler(handler)

    def remove_handler(self, handler):
        """
        Remove the given handler from the list of handler.
        Unknown handlers are ignored.
        """
        self.logger.removeHandler(handler)

    def log_debug(self, message):
        """Convenient method to log a debug-level message."""
        # shortcut instead of delegating this to the logging library
        if not self.logger.disabled:
            self.logger.log(logging.DEBUG, message)

    def log(self, level, message, *args, **kwargs):
        """Forward the message to the wrapped logger."""
        self.logger.log(level, message, *args, **kwargs)


fritzlogger = FritzLogger()
