"""
Logging interface for the fritzconnection library.

On module level an instance of `FritzLogger` gets created as `fritzlogger`
that can get imported by:

>>> from fritzconnection.core.logger import fritzlogger

The fritzlogger instance is preset to report on DEBUG level, the default
handler is the NullHandler. To do some logging, a handler must be
provided:

>>> fritzlogger.add_handler(the_handler)
>>> fritzlogger.log("the message")  # will get logged now

In case that another logger is already in use, the other logger can get
set as parent for fritzlogger. fritzlogger will then use the parent
handlers.

>>> fritzlogger.set_parent(another_logger)
>>> fritzlogger.log("the message")  # will get logged now

For convenience fritzlogger provides the methods `set_streamhandler` and
`set_filehandler` to add predefined handlers.

If logging is activated at debug-level, fritzconnection will log all
requests and responses. This can produce a lot of output, especial on
initializing a FritzConnection-instance. To suppress output the methods
`disable` and `enable` can get called. Default mode is enable.

"""

import logging


class FritzLogger:
    """
    Wrapper for the logging library to reduce executable code on module
    global level. As multiple instances would use the same logger, to not
    get confused this class is a singleton.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Takes care to be a singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, level=logging.DEBUG):
        """Creates the internal logger state."""
        self.logger = logging.getLogger("fritzconnection")
        self.logger.addHandler(logging.NullHandler())
        self.loggers = {
            logging.CRITICAL: self.logger.critical,
            logging.ERROR: self.logger.error,
            logging.WARNING: self.logger.warning,
            logging.INFO: self.logger.info,
            logging.DEBUG: self.logger.debug,
            "critical": self.logger.critical,
            "error": self.logger.error,
            "warning": self.logger.warning,
            "info": self.logger.info,
            "debug": self.logger.debug,
        }
        self.set_level(level)

    def set_level(self, level):
        """Set the log-level for the logger."""
        self.logger.setLevel(level)

    def set_parent(self, parent):
        """
        Set a parent manually.

        After calling all registered handlers FritzLogger will call the
        handlers of the parent chain (which must also all be loggers).
        Be careful not to create a closed loop of parents!
        """
        self.logger.parent = parent

    def delete_parent(self):
        """Deletes the parent logger."""
        self.logger.parent = None

    def disable(self):
        """Disables the logger."""
        self.logger.disabled = True

    def enable(self):
        """Enables the logger."""
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

    def log(self, message, level=logging.DEBUG, **kwargs):
        """
        Send the message to the logger. Unknown levels are ignored.
        """
        if isinstance(level, str):
            level = level.lower()
        logger = self.loggers.get(level)
        if logger:
            logger(message, **kwargs)


fritzlogger = FritzLogger()
