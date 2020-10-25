"""
Module to access call monitor: started, finished, incoming and outgoing calls.
"""
from datetime import datetime
import logging
from socket import (
    AF_INET,
    SO_KEEPALIVE,
    SOCK_STREAM,
    SOL_SOCKET,
    socket,
    timeout as SocketTimeout,
)
from threading import Event as ThreadingEvent, Thread
from time import sleep

_LOGGER = logging.getLogger(__name__)

INTERVAL_RECONNECT = 60


class FritzCallMonitor:
    """Event listener to monitor calls on the Fritz!Box."""

    def __init__(self, address="169.254.1.1", port=1012, callback=None):
        """Initialize Fritz!Box call monitor instance."""
        self.address = address
        self.port = port
        self.callback = callback
        self.sock = None
        self.stopped = ThreadingEvent()

    def connect(self):
        """Connect to the Fritz!Box."""
        _LOGGER.debug("Setting up socket...")
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(10)
        self.sock.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
        try:
            self.sock.connect((self.address, self.port))
            Thread(target=self._listen).start()
        except OSError as err:
            self.sock = None
            _LOGGER.error(
                "Cannot connect to %s on port %s: %s", self.address, self.port, err
            )

    def _listen(self):
        """Listen to incoming or outgoing calls."""
        _LOGGER.debug("Connection established, waiting for response...")
        while not self.stopped.is_set():
            try:
                response = self.sock.recv(2048)
            except SocketTimeout:
                # if no response after 10 seconds, just recv again
                continue
            response = str(response, "utf-8")
            _LOGGER.debug("Received %s", response)

            if not response:
                # if the response is empty, the connection has been lost.
                # try to reconnect
                _LOGGER.warning("Connection lost, reconnecting...")
                self.sock = None
                while self.sock is None:
                    self.connect()
                    sleep(INTERVAL_RECONNECT)
            else:
                line = response.split("\n", 1)[0]
                self._parse(line)
                sleep(1)

    def _parse(self, line):
        """Parse the call information and call callback function with extracted data."""
        line = line.split(";")
        df_in = "%d.%m.%y %H:%M:%S"
        df_out = "%Y-%m-%dT%H:%M:%S"
        isotime = datetime.strptime(line[0], df_in).strftime(df_out)

        if line[1] == "RING":
            data = {
                "type": "incoming",
                "from": line[3],
                "to": line[4],
                "device": line[5],
                "initiated": isotime,
                "from_name": line[3],
            }
            self.callback(data)

        elif line[1] == "CALL":
            data = {
                "type": "outgoing",
                "from": line[4],
                "to": line[5],
                "device": line[6],
                "initiated": isotime,
                "to_name": line[5],
            }
            self.callback(data)

        elif line[1] == "CONNECT":
            data = {
                "type": "started",
                "with": line[4],
                "device": line[3],
                "accepted": isotime,
                "with_name": line[4],
            }
            self.callback(data)

        elif line[1] == "DISCONNECT":
            data = {"type": "finished", "duration": line[3], "closed": isotime}
            self.callback(data)