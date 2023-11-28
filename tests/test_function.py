import time


def _do_work_light():
    time.sleep(10)


def _do_work_heavy():
    time.sleep(60)


def test_1():
  _do_work_light()


def test_2():
  _do_work_light()


def test_3():
  _do_work_light()


def test_4():
  _do_work_light()


def test_5():
  _do_work_light()


def test_6():
  _do_work_light()


def test_7():
  _do_work_heavy()


def test_8():
  _do_work_heavy()


def test_9():
  _do_work_heavy()


def test_10():
  _do_work_heavy()
