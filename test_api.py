def test_get(x, y):
    res = 0
    if x > 0 and y > 0:
        res = x
    return res


def test_post(x, y):
    res = 0
    match = True
    if match:
        res = 1 << 2
    else:
        res = 1 >> 2
    return res


def test_del(x, y):
    if x > y:
        return 0
    match = x > y
    if match:
        res = 0b0011 << 2
    else:
        res = 0b1101 >> 2
    return res
