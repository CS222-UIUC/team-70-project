# pylint: skip-file

def func(x):
    return x + 1

def test_answer():
    assert func(3) != 5

def test_again():
    assert func(3) == 4
    assert func(0) == 1

def how_work():
    assert False