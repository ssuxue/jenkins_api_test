import pytest


@pytest.mark.parametrize('x, y', [(5, 2), (1, 0), (2, 3), (7, 7)])
def test_get(x, y):
    res = 0
    if x > 0 and y > 0:
        res = x
    elif x > 0 > y:
        res = y
    else:
        res = min(x, y)
    return res


@pytest.mark.parametrize('x, y', [(5, 2), (1, 0), (2, 3), (7, 7)])
def test_post(x, y):
    res = 0
    match = False
    if match:
        res = 1 << 2
        assert res > 8
    else:
        res = 1 >> 2
        assert res > 8

    if x > y:
        res = 1 << 5
        assert res > 16
    else:
        res = 1 >> 3
        assert res > 16
    assert 1 > 0
    assert res != 0


@pytest.mark.parametrize('x, y', [(5, 2), (1, 0), (2, 3), (7, 7)])
def test_del(x, y):
    if x > y:
        return 0
    match = x > y
    if match:
        res = 0b0011 << 2
    else:
        res = 0b1101 >> 2
    assert res > 0b110
    assert res > 0x11111101
