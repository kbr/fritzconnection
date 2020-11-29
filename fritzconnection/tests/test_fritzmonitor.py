import queue
import socket
import threading
import time

import pytest

from ..core.fritzmonitor import FritzMonitor, EventReporter


class MockSocket:
    """
    A socket dummy to simulate receiving data and optional timeouts.
    """

    def __init__(self, mock_data=None, timeout=None, raise_connect_timeout=False):
        self.mock_data = mock_data
        self.timeout = timeout
        self.raise_connect_timeout = raise_connect_timeout

    def connect(self, *args):
        if self.raise_connect_timeout:
            raise socket.timeout("mock failed socket.connect")

    def close(self):
        pass

    def recv(self, chunk_size=None):
        if not self.mock_data:
            if self.timeout:
                time.sleep(self.timeout)
            raise socket.timeout("mock timeout")
        if chunk_size is None:
            chunk = self.mock_data.encode("utf-8")
        else:
            chunk = self.mock_data[:chunk_size]
            self.mock_data = self.mock_data[chunk_size:]
        return chunk.encode("utf-8")


class MockReconnectSocket(MockSocket):
    """
    Dummy socket to simulate a single reconnect.
    """

    def __init__(self, mock_data=None):
        self.data_provider = self._returner(mock_data)
        self.connect_called_num = 0

    def connect(self, *args):
        self.connect_called_num += 1

    def recv(self, chuck_size=None):
        try:
            data = next(self.data_provider)
        except StopIteration:
            data = " "
        return data.encode("utf-8")

    @staticmethod
    def _returner(mock_data):
        for data in mock_data:
            yield data


class MockReconnectFailSocket(MockReconnectSocket):
    """
    Dummy socket to simulate multiple faild reconnections.  
    """

    def __init__(self, mock_data=None, timeouts=0):
        super().__init__(mock_data)
        self._connector = self.connector(timeouts)

    def connect(self, *args):
        super().connect(*args)
        if not next(self._connector):
            raise socket.timeout("mock reconnect timeout")

    @staticmethod
    def connector(timeouts):
        yield True
        for _ in range(timeouts):
            yield False
        while True:
            yield True


def test_init_fritzmonitor():
    fm = FritzMonitor()
    assert fm.monitor_thread == None
    assert fm.stop_flag.is_set() == False


@pytest.mark.parametrize(
    "data, expected",
    [
        ("some data", None),
        ("some_data\nmore_data", "some_data"),
        ("some\nmore\ndata", "some more"),
        ("2019;10\n11:30\ncall\n123\nmore", "2019;10 11:30 call 123"),
    ],
)
def test_event_reporter(data, expected):
    q = queue.Queue()
    ep = EventReporter(q)
    ep.add(data)
    if expected is None:
        # no data should be in the queue
        assert pytest.raises(queue.Empty, q.get_nowait)
    else:
        for event in expected.split():
            item = q.get_nowait()
            assert item == event


def test_start_stop():
    mock_socket = MockSocket(timeout=0.01)
    fm = FritzMonitor()
    assert fm.monitor_thread is None
    fm.start(sock=mock_socket)
    assert fm.monitor_thread is not None
    assert fm.monitor_thread.is_alive() is True
    thread = fm.monitor_thread
    fm.stop()
    assert thread.is_alive() is False
    assert fm.monitor_thread is None


def test_start_stop_properties():
    mock_socket = MockSocket(timeout=0.01)
    fm = FritzMonitor()
    assert fm.has_monitor_thread is False
    assert fm.is_alive is False
    _ = fm.start(sock=mock_socket)
    assert fm.has_monitor_thread is True
    assert fm.is_alive is True
    fm.stop()
    assert fm.has_monitor_thread is False
    assert fm.is_alive is False


def test_queue_and_threading_instances():
    mock_socket = MockSocket(timeout=0.01)
    fm = FritzMonitor()
    event_queue = fm.start(sock=mock_socket)
    assert isinstance(event_queue, queue.Queue)
    assert isinstance(fm.monitor_thread, threading.Thread)
    fm.stop()


def test_start_twice():
    """
    It is a failure to start a running instance again.  
    """
    mock_socket = MockSocket(timeout=0.01)
    fm = FritzMonitor()
    fm.start(sock=mock_socket)
    with pytest.raises(RuntimeError):
        # start running instance again: should raise a RuntimeError
        fm.start(sock=mock_socket)
    fm.stop()
    # but starting now again should work:
    fm.start(sock=mock_socket)
    fm.stop()


def test_failed_connection():
    mock_socket = MockSocket(raise_connect_timeout=True)
    fm = FritzMonitor()
    pytest.raises(OSError, fm.start, sock=mock_socket)


@pytest.mark.parametrize(
    "mock_data, chunk_size, expected_events",
    [
        ("simple string of words\n", None, "simple string of words"),
        ("event;call\nnumber\n12345\n", None, "event;call|number|12345"),
        (
            "CALL;20201031;12;34\nINC;20-10-31;09;76\n",
            None,
            "CALL;20201031;12;34|INC;20-10-31;09;76",
        ),
        ("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n", None, "1|2|3|4|5|6|7|8|9|10|11"),
        ("simple string of words\n", 2048, "simple string of words"),
        ("event;call\nnumber\n12345\n", 2048, "event;call|number|12345"),
        (
            "CALL;20201031;12;34\nINC;20-10-31;09;76\n",
            2048,
            "CALL;20201031;12;34|INC;20-10-31;09;76",
        ),
        ("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n", 2048, "1|2|3|4|5|6|7|8|9|10|11"),
        ("simple string of words\n", 20, "simple string of words"),
        ("event;call\nnumber\n12345\n", 20, "event;call|number|12345"),
        (
            "CALL;20201031;12;34\nINC;20-10-31;09;76\n",
            20,
            "CALL;20201031;12;34|INC;20-10-31;09;76",
        ),
        ("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n", 20, "1|2|3|4|5|6|7|8|9|10|11"),
        ("simple string of words\n", 2, "simple string of words"),
        ("event;call\nnumber\n12345\n", 2, "event;call|number|12345"),
        (
            "CALL;20201031;12;34\nINC;20-10-31;09;76\n",
            2,
            "CALL;20201031;12;34|INC;20-10-31;09;76",
        ),
        ("1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n", 2, "1|2|3|4|5|6|7|8|9|10|11"),
    ],
)
def test_get_events(mock_data, chunk_size, expected_events):
    mock_socket = MockSocket(mock_data=mock_data, timeout=0.01)
    fm = FritzMonitor()
    event_queue = fm.start(sock=mock_socket)
    thread = fm.monitor_thread
    received_event_num = 0
    for n, expected_event in enumerate(expected_events.split("|"), start=1):
        try:
            assert event_queue.get(timeout=0.1) == expected_event
            received_event_num += 1
        except queue.Empty:
            pass
    # check if alle expected events have been received
    assert received_event_num == n
    fm.stop()
    assert thread.is_alive() is False


def test_reconnect():
    data = ["first\n", "", "second\n"]
    mock_socket = MockReconnectSocket(data)
    fm = FritzMonitor()
    event_queue = fm.start(sock=mock_socket, reconnect_delay=0.001)
    for expected in [data[0], data[2]]:
        # should not raise _queue.Empty:
        assert event_queue.get(timeout=0.1) == expected.strip()
    fm.stop()
    assert mock_socket.connect_called_num == 2


@pytest.mark.parametrize(
    "timeouts, tries, expected_result",
    [
        (0, 0, True),
        (0, 1, True),
        (1, 1, False),
        (1, 2, True),
        (4, 5, True),
        (5, 5, False),
        (6, 5, False),
    ],
)
def test_MockReconnectFailSocket(timeouts, tries, expected_result):
    """
    Internal test to check whether the MockReconnectFailSocket class works as expected.
    """
    sock = MockReconnectFailSocket(timeouts=timeouts)
    assert sock.connect_called_num == 0
    sock.connect()
    assert sock.connect_called_num == 1
    result = True  # got connection
    for cycle in range(tries):
        try:
            sock.connect()
        except OSError:
            result = False
        else:
            result = True
            break
        finally:
            assert (
                sock.connect_called_num == cycle + 2
            )  # cycle is zero based plus initional connection
    assert result == expected_result


@pytest.mark.parametrize(
    "timeouts", list(range(6)),
)
def test__get_connected_socket(timeouts):
    socket = MockReconnectFailSocket(timeouts=timeouts)
    fm = FritzMonitor()
    s = fm._get_connected_socket(sock=socket)  # make initional connection
    assert s == socket
    for _ in range(timeouts):
        with pytest.raises(OSError):
            fm._get_connected_socket(sock=socket)
    fm._get_connected_socket(sock=socket)


@pytest.mark.parametrize(
    "timeouts, tries, expected_result",
    [
        (0, 0, False),
        (0, 1, True),
        (1, 0, False),
        (1, 1, False),
        (1, 2, True),
        (4, 5, True),
        (5, 5, False),
        (6, 5, False),
    ],
)
def test__reconnect_socket(timeouts, tries, expected_result):
    mock_socket = MockReconnectFailSocket(timeouts=timeouts)
    fm = FritzMonitor()
    socket = fm._get_connected_socket(sock=mock_socket)  # make initional connection
    result = fm._reconnect_socket(
        sock=socket, reconnect_delay=0.001, reconnect_tries=tries
    )
    assert result == expected_result


@pytest.mark.parametrize(
    "data, timeouts, tries, success",
    [
        (["first\n", "second\n"], 0, 0, True),
        (["first\n", "", "second\n"], 1, 0, False),
        (["first\n", "", "second\n"], 0, 1, True),
        (["first\n", "", "second\n"], 1, 1, False),
        (["first\n", "", "second\n"], 1, 2, True),
        # default for tries: 5
        (["first\n", "", "second\n"], 3, 5, True),
        (["first\n", "", "second\n"], 4, 5, True),
        (["first\n", "", "second\n"], 5, 5, False),
    ],
)
def test_terminate_thread_on_failed_reconnection(data, timeouts, tries, success):
    """
    Check for thread-termination in case reconnection fails.
    """
    mock_socket = MockReconnectFailSocket(data, timeouts=timeouts)
    fm = FritzMonitor()
    fm.start(sock=mock_socket, reconnect_delay=0.001, reconnect_tries=tries)
    # give thread some time:
    time.sleep(0.01)
    if success:
        assert fm.is_alive is True
    else:
        assert fm.is_alive is False
        assert fm.monitor_thread is None
    fm.stop()


def test_restart_failed_monitor():
    """
    Check whether a fritzmonitor instance with a lost connection can get started again.
    Starting the same instance twice does (and should) not work.
    See test_start_twice().
    But after a failed reconnect (a lost connection) the same instance without calling stop()
    """
    socket = MockReconnectFailSocket(
        mock_data=["first\n", "", "second\n"], timeouts=16
    )  # just some timeouts
    fm = FritzMonitor()
    fm.start(
        sock=socket, reconnect_delay=0.001, reconnect_tries=5
    )  # set default explicit for clarity
    # give socket some time to lose connection:
    time.sleep(0.01)
    assert fm.is_alive is False
    assert fm.stop_flag.is_set() is False
    # dont' call stop here!
    # fm.stop()
    socket = MockSocket(timeout=0.01)  # socket not losing connection
    # should not trigger a RuntimeError
    fm.start(
        sock=socket, reconnect_delay=0.001, reconnect_tries=5
    )  # set default explicit for clarity
    assert fm.is_alive is True
    fm.stop()


def test_context_manager():
    sock = MockSocket(timeout=0.01)
    with FritzMonitor() as fm:
        fm.start(sock=sock)
        assert fm.is_alive is True
    assert fm.is_alive is False
