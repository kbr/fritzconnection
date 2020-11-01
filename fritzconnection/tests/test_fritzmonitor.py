import queue
import socket
import threading
import time

import pytest

from ..core.fritzmonitor import FritzMonitor, EventReporter


class MockSocket:
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
    event_queue = fm.start(sock=mock_socket)
    assert isinstance(event_queue, queue.Queue)
    assert isinstance(fm.monitor_thread, threading.Thread)
    assert fm.monitor_thread.is_alive() is True
    thread = fm.monitor_thread
    fm.stop()
    assert thread.is_alive() is False
    assert fm.monitor_thread is None


def test_start_twice():
    mock_socket = MockSocket(timeout=0.01)
    fm = FritzMonitor()
    _ = fm.start(sock=mock_socket)
    pytest.raises(RuntimeError, fm.start)
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
