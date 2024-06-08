import pyoload

from pyoload import Cast
from pyoload import annotable
from pyoload import annotate
from pyoload import is_annotable
from pyoload import is_annoted
from pyoload import unannotable
from pyoload import unannotate

assert pyoload.__version__ == "2.0.0"


@annotate
def foo(a, b=3, c: str = "R") -> int:
    assert b == 3
    assert isinstance(c, str)
    return 3


def foo1(a: Cast(str)):
    return a


def test_annotate():
    foo(2)
    assert annotate(foo1)(3) == '3'
    assert unannotate(annotate(foo1))(3) == 3
    assert annotate(unannotable(foo1))(3) == 3
    assert annotate(unannotable(foo1))(3) == 3
    assert annotate(unannotable(foo1), force=True)(3) == '3'
    assert annotate(annotable(unannotable(foo1)))(3) == '3'
    assert is_annotable(foo1)
    assert is_annotable(annotable(foo1))
    assert is_annotable(annotable(unannotable(foo1)))
    assert not is_annotable(unannotable(foo1))
    assert is_annoted(annotate(foo1, force=True))
    assert not is_annoted(foo1)


if __name__ == "__main__":
    test_annotate()
