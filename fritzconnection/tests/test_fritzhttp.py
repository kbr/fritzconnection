
from http import HTTPStatus
from types import SimpleNamespace

import pytest

from ..core.fritzhttp import FritzHttp


CHALLENGE_XML = "<SessionInfo><Challenge>1234abcd</Challenge></SessionInfo>"
SID_XML = "<SessionInfo><SID>0123456789abcdef</SID></SessionInfo>"


class MockResponse:
    """
    Minimal stand-in for a requests-response, usable as a
    contextmanager like the real one.
    """
    def __init__(self, text="", status_code=HTTPStatus.OK):
        self.text = text
        self.status_code = status_code
        self.headers = {"content-type": "text/xml"}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class MockSession:
    """
    Session stub recording every get() and post() call as a
    (method, url, kwargs) tuple. Takes the responses to hand out, in
    the order of the calls; the last one is repeated.
    """
    def __init__(self, responses=None):
        self.responses = list(responses) if responses else [MockResponse()]
        self.calls = []

    def _next_response(self):
        if len(self.responses) > 1:
            return self.responses.pop(0)
        return self.responses[0]

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        return self._next_response()

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return self._next_response()

    @property
    def timeouts(self):
        """The timeout argument of every recorded call, in call order."""
        return [kwargs.get("timeout", "not given") for _, _, kwargs in self.calls]


def get_fritzhttp(session, timeout=None):
    """
    Returns a FritzHttp instance bound to a fake connection that uses
    the given session stub and the given timeout.
    """
    fc = SimpleNamespace(
        address="http://192.168.178.1",
        session=session,
        soaper=SimpleNamespace(user="user", password="password"),
        timeout=timeout,
    )
    return FritzHttp(fc)


@pytest.mark.parametrize("timeout", [None, 10, 2.5, (3, 7)])
def test_call_url_forwards_the_timeout(timeout):
    """
    The connection timeout is documented as a global setting, so the
    aha-http-interface must apply it to its data requests as well.
    """
    session = MockSession([MockResponse(text="data")])
    fh = get_fritzhttp(session, timeout=timeout)
    fh.sid = "sid"  # skip the login roundtrip

    fh.call_url("http://192.168.178.1:80/query.lua", {})

    assert session.timeouts == [timeout]


@pytest.mark.parametrize("timeout", [None, 10, 2.5, (3, 7)])
def test_login_requests_forward_the_timeout(timeout):
    """
    Obtaining a session id takes two requests (challenge and response).
    Neither of them may be able to block forever either.
    """
    session = MockSession(
        [MockResponse(text=CHALLENGE_XML), MockResponse(text=SID_XML)]
    )
    fh = get_fritzhttp(session, timeout=timeout)

    fh._set_sid_from_box()

    assert fh.sid == "0123456789abcdef"
    assert [method for method, _, _ in session.calls] == ["get", "post"]
    assert session.timeouts == [timeout, timeout]
