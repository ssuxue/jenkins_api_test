import pytest


@pytest.mark.parametrize('x, y', [(2, 3), (7, 7)])
def test_get(x, y):
    res = 0
    if x > 0 and y > 0:
        res = x
        assert 1 == 1
    assert res == x
    return res


def test_assert1():
    assert 1 == 0


def test_assert2():
    assert 1 > 0
    assert 2 > 1
    assert 6 == 0b110
    assert 3 > 1


def test_assert3():
    assert 0x110 == 6


@pytest.mark.parametrize('x, y', [(5, 2), (7, 7)])
def test_post(x, y):
    res = 0
    match = True
    if match:
        res = 1 << 2
    else:
        res = 1 >> 2
    assert x / y < res
    assert x // y > 1


@pytest.mark.parametrize('x, y', [(5, 2), (1, 0), (2, 3), (7, 7)])
def test_del(x, y):
    if x > y:
        assert 1 == 0
    match = x > y
    if match:
        res = 0b0011 << 2
    else:
        res = 0b1101 >> 2
    assert res >= 0
    assert x + y >= res
    assert x + y > 0
    assert y > x

def test_api_up():
    assert 1 == 1
