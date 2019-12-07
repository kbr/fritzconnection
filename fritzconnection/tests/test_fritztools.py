import pytest

from ..lib.fritztools import format_num, format_rate


@pytest.mark.parametrize(
    "num, formated_num", [
        (300, '300.0 bytes'),
        (2048, '2.0 KB'),
        (3000, '2.9 KB'),
        (32500, '31.7 KB'),
        (45e6, '42.9 MB'),
        (45e9, '41.9 GB'),
        (45e12, '40.9 TB'),
        (45e15, '40.0 PB'),
    ]
)

def test_format_num(num, formated_num):
    assert formated_num == format_num(num)

