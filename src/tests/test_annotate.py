import pyoload

from pyoload import annotate

assert pyoload.__version__ == "2.0.0"


@annotate
def foo(a, b=3, c: str = "R") -> int:
    assert b == 3
    assert isinstance(c, str)
    return 3


def test_annotate():
    foo(2)


if __name__ == "__main__":
    test_annotate()
