"""
Module to communicate with the AVM Fritz!Box service providing real time
phone-call events.

To run fritzmonitor, the CallMonitor service of the box has to be activated.
This can be done with any registered Phone by typing the following codes:
activate: #96*5*
deactivate: #96*4*
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import queue
import socket
import threading
import time


FRITZ_IP_ADDRESS = "169.254.1.1"
FRITZ_MONITOR_PORT = 1012
FRITZ_MONITOR_QUEUE_SIZE = 256
FRITZ_MONITOR_CHUNK_SIZE = 1024 * 4
FRITZ_MONITOR_SOCKET_TIMEOUT = 10

MIN_RECONNECT_DELAY = 0.02  # minimum delay in seconds
MAX_RECONNECT_DELAY = 60  # maximum delay in seconds
RECONNECT_DELAY_FACTOR = 10  # factor to increase delays between reconnection tries
RECONNECT_TRIES = 10  # number of tries to reconnect before giving up


class EventReporter:
    """
    Takes a Queue and implements a buffer for line-separated data.
    If at least one line is in the buffer, the line gets put into the
    Queue for further processing elsewhere (by a routine reading the queue).
    """

    def __init__(
        self,
        monitor_queue: queue.Queue,
        block_on_filled_queue: bool = False
    ):
        """
        Takes the monitor queue (of type queue.Queue) and a boolean
        'block_on_filled_queue'. If 'block_on_filled_queue' is True the thread
        will wait until a free slot is available blocking the thread reading
        call_monitor events from the socket connected to the Fritz!Box.
        """
        self.buffer = ""
        self.monitor_queue = monitor_queue
        self.block_on_filled_queue = block_on_filled_queue

    def add(self, data: str) -> None:
        """
        Adds the given 'data' to the buffer. If the buffer holds at least one
        line (separated by newline-character), the line (or lines) are put into the
        'monitor_queue' as events to be processed from a reader elsewhere.
        """
        self.buffer += data
        *parts, self.buffer = self.buffer.split("\n")
        for part in parts:
            try:
                self.monitor_queue.put(part, block=self.block_on_filled_queue)
            except queue.Full:
                # ignore
                pass


class FritzMonitor:
    """
    Monitor Fritz!Box events about started, finished, incoming and outgoing
    calls.
    """

    def __init__(
        self,
        address: str = FRITZ_IP_ADDRESS,
        port: int = FRITZ_MONITOR_PORT,
        timeout: int = FRITZ_MONITOR_SOCKET_TIMEOUT,
        encoding: str = "utf-8",
    ):
        self.address = address
        self.port = port
        self.timeout = timeout
        self.encoding = encoding
        self.stop_flag = threading.Event()
        self.monitor_thread: threading.Thread | None = None
        self.mock_socket = None  # for testing

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    @property
    def has_monitor_thread(self) -> bool:
        """
        Returns True if a monitor-thread has been created.
        That should be the case after calling start() and before calling stop().
        """
        return bool(self.monitor_thread)

    @property
    def is_alive(self) -> bool:
        """
        Returns True if there is a monitor-thread and the thread is running.
        Returns False otherwise.
        """
        return self.has_monitor_thread and self.monitor_thread.is_alive()  # type: ignore

    def start(
        self,
        queue_size: int = FRITZ_MONITOR_QUEUE_SIZE,
        block_on_filled_queue: bool = False,
        reconnect_delay: float = MAX_RECONNECT_DELAY,
        reconnect_tries: float = RECONNECT_TRIES,
        sock=None,
    ) -> queue.Queue:
        """
        Start the monitor thread and return a Queue instance with the
        given size to report the call_monitor events. Events are of type
        string. Raises an `OSError` if the socket can not get connected
        in a given timeout. Raises a `RuntimeError` if start() get
        called a second time without calling stop() first. `queue_size`
        is the number of events the queue can store. If
        `block_on_filled_queue` is False the event will get discarded in
        case of no free block (default). On True the EventReporter will
        block until a slot is available. `reconnect_delay` defines the
        maximum time interval in seconds between reconnection tries, in
        case that a socket-connection gets lost. `reconnect_tries`
        defines the number of consecutive to reconnect a socket before
        giving up. `sock` is used for testing to inject a mock-socket.
        """
        if self.monitor_thread:
            # It's an error to create a second thread for monitoring
            raise RuntimeError("A FritzMonitor thread is already running")
        self.mock_socket = sock
        # get socket or raise OSError in main thread:
        sock = self._get_connected_socket()
        monitor_queue = queue.Queue(maxsize=queue_size)  # type: ignore
        kwargs = {
            "monitor_queue": monitor_queue,
            "sock": sock,
            "block_on_filled_queue": block_on_filled_queue,
            "reconnect_delay": reconnect_delay,
            "reconnect_tries": reconnect_tries,
        }
        # clear event object in case the instance gets 'reused':
        self.stop_flag.clear()
        self.monitor_thread = threading.Thread(target=self._monitor, kwargs=kwargs)
        self.monitor_thread.start()
        return monitor_queue

    def stop(self) -> None:
        """
        Stop the current running monitor_thread.
        """
        if self.monitor_thread:
            if self.monitor_thread.is_alive():
                self.stop_flag.set()  # tell thread to terminate
                self.monitor_thread.join()  # wait for termination without timeout
            self.monitor_thread = None

    def _get_connected_socket(self):
        """
        Return a new created socket.
        In case of failure an OSError is raised.
        """
        # use a mock socket for tests
        if self.mock_socket:
            sock = self.mock_socket
        else:
            sock = socket.socket()
            # these options should work on all platforms:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # socket actions can fail for different reasons,
            # without a timeout they can hang a long time.
            sock.settimeout(self.timeout)
        try:
            sock.connect((self.address, self.port))
        except socket.timeout:
            # will fail if the address:port is not available (not present or in use)
            # socket.timeout is subclass of OSError, so it is save to raise an OSError
            msg = f"Unable to connect to '{self.address}:{self.port}'"
            raise OSError(msg)
        return sock

    def _reconnect_socket(
        self,
        max_reconnect_delay=MAX_RECONNECT_DELAY,
        reconnect_tries=RECONNECT_TRIES,
    ):
        """
        Try to reconnect a lost connection.
        Returns a new socket on success and None otherwise.
        """
        reconnect_delay = self._delayer(max_delay=max_reconnect_delay)
        while reconnect_tries > 0:
            next(reconnect_delay)
            try:
                return self._get_connected_socket()
            except OSError:
                reconnect_tries -= 1
        return None

    def _monitor(
        self,
        monitor_queue,
        sock,
        block_on_filled_queue,
        reconnect_delay,
        reconnect_tries,
    ):
        """
        The internal monitor routine running in a separate thread.
        """
        # Instantiate an EventReporter to push event to the event_queue.
        event_reporter = EventReporter(
            monitor_queue=monitor_queue, block_on_filled_queue=block_on_filled_queue
        )
        while not self.stop_flag.is_set():
            try:
                raw_data = sock.recv(FRITZ_MONITOR_CHUNK_SIZE)
            except socket.timeout:
                # without a timeout an open socket will never return from a
                # connection closed by a router (may be of limited resources).
                # Therefore be sure to set a timeout at socket creation (elsewhere).
                # So just try again after timeout.
                continue
            if not raw_data:
                # empty response indicates a lost connection.
                # try to reconnect.
                sock = self._reconnect_socket(
                    max_reconnect_delay=reconnect_delay,
                    reconnect_tries=reconnect_tries,
                )
                if sock is None:
                    # reconnect has failed: terminate the thread
                    break
            else:
                # sock.recv returns a bytearray to decode:
                response = raw_data.decode(self.encoding)
                event_reporter.add(response)
        # clean up on terminating thread:
        try:
            sock.close()
        except (AttributeError, OSError):
            pass
        # reset monitor_thread to be able to restart
        self.monitor_thread = None

    @staticmethod
    def _delayer(
        min_delay=MIN_RECONNECT_DELAY,
        max_delay=MAX_RECONNECT_DELAY,
        multiplier=RECONNECT_DELAY_FACTOR,
    ):
        """
        delay generator with increasing sleep-times.
        """
        delay = min(min_delay, max_delay)
        while True:
            time.sleep(delay)
            yield
            delay = min(delay * multiplier, max_delay)


