import sys
from types import SimpleNamespace
from unittest import mock

import pytest

from ..cli.utils import get_cli_arguments, get_instance


@pytest.mark.parametrize(
    "argv, expected", [
        ([], False),
        (["--public-connection"], True),
    ]
)
def test_cli_public_connection_flag(argv, expected):
    with mock.patch.object(sys, "argv", ["fritzconnection"] + argv):
        args = get_cli_arguments()
    assert args.public_connection is expected

    cls = mock.MagicMock()
    get_instance(cls, args)
    _, kwargs = cls.call_args
    assert kwargs["use_public_connection"] is expected


def test_get_instance_without_public_connection_argument():
    """Argument namespaces created without the new flag keep working."""
    args = SimpleNamespace(
        address="192.168.178.1", port=None, username=None, password=None,
        encrypt=False, use_cache=False, verify_cache=True,
        cache_directory=None, cache_format=None,
    )
    cls = mock.MagicMock()
    get_instance(cls, args)
    _, kwargs = cls.call_args
    assert kwargs["use_public_connection"] is False
