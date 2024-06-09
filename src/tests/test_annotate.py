import pyoload

from pyoload import AnnotationResolutionError
from pyoload import Cast
from pyoload import annotable
from pyoload import annotate
from pyoload import is_annotable
from pyoload import is_annoted
from pyoload import resove_annotations
from pyoload import type_match
from pyoload import unannotable
from pyoload import unannotate

assert pyoload.__version__ == "2.0.0"


@annotate
def foo(a, b=3, c: str = "R") -> Cast(int):
    assert b == 3
    assert isinstance(c, str)
    return '3'


def foo1(a: Cast(str)):
    return a


@annotate
class MyCLass:
    __slots__ = ('a', 'b')
    a: 'int'
    b: 'str'


def test_annotate():
    assert foo(2) == 3
    assert annotate(foo1)(3) == "3"
    assert unannotate(annotate(foo1))(3) == 3
    assert annotate(unannotable(foo1))(3) == 3
    assert annotate(unannotable(foo1))(3) == 3
    assert annotate(unannotable(foo1), force=True)(3) == "3"
    assert annotate(annotable(unannotable(foo1)))(3) == "3"
    assert is_annotable(foo1)
    assert is_annotable(annotable(foo1))
    assert is_annotable(annotable(unannotable(foo1)))
    assert not is_annotable(unannotable(foo1))
    assert is_annoted(annotate(foo1, force=True))
    assert not is_annoted(foo1)

    try:
        @annotate
        def footy(a: 'Nothing here'):
            pass

        footy(2)
    except AnnotationResolutionError:
        pass
    else:
        raise Exception()
    try:
        @annotate
        class Footy:
            a: 'Nothing here'

        Footy().a = 4
    except AnnotationResolutionError:
        pass
    else:
        raise Exception()

    try:
        assert type_match({3: None}, dict[str]) == (True, None)
    except Exception:
        assert type_match({3: None}, dict[int]) == (True, None)
    else:
        raise Exception()

    obj = MyCLass()
    try:
        obj.b = 3
    except Exception:
        obj.a = 3
        obj.b = '7'
    else:
        raise Exception()

    try:
        resove_annotations(None)
    except AnnotationResolutionError:
        pass
    else:
        raise Exception()

    @annotate
    def fooar(a: 'str', b: 'int'):
        pass
    fooar('4', 3)
    try:
        fooar('4', '4')
    except Exception:
        pass
    else:
        raise Exception()


if __name__ == "__main__":
    test_annotate()
