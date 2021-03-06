import pytest

from ..lib.fritztools import byte_formatter, format_num


@pytest.mark.parametrize(
    "value, result, dimension", [
        (1, 1.0, 'B'),
        (123, 123.0, 'B'),
        (1230, 1.230, 'KB'),
        (12345, 12.345, 'KB'),
        (242981246, 242.981246, 'MB'),
        (24298124612, 24.298124612, 'GB'),
        (2429812461200, 2.4298124612, 'TB'),
        (42e3, 42.0, 'KB'),
        (42e6, 42.0, 'MB'),
        (42e9, 42.0, 'GB'),
        (42e12, 42.0, 'TB'),
        (42e15, 42.0, 'PB'),
        (42e18, 42000.0, 'PB'),
        (1.0, 1.0, 'B'),
        (0.1, 0, 'B'),
        (0.01, 0, 'B'),
        (0.001, 0, 'B'),
        (0, 0, 'B'),
        (-10, 10, 'B'),
    ]
)
def test_byte_formatter(value, result, dimension):
    num, dim = byte_formatter(value)
    assert num == result
    assert dim == dimension


@pytest.mark.parametrize(
    "num, formated_num", [
        (300, '300.0 B'),
        (2000, '2.0 KB'),
        (3500, '3.5 KB'),
        (32500, '32.5 KB'),
        (242911246, '242.9 MB'),
        (242981246, '243.0 MB'),
        (45e6, '45.0 MB'),
        (45e9, '45.0 GB'),
        (45e12, '45.0 TB'),
        (45e15, '45.0 PB'),
        (45e18, '45000.0 PB'),
    ]
)
def test_format_num(num, formated_num):
    assert formated_num == format_num(num)


def test_format_num_bits():
    result = format_num(1234, unit='bits')
    assert result == '1.2 KBit'
