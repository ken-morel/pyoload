import pyoload

from pyoload import AnnotationError
from pyoload import AnnotationResolutionError
from pyoload import Cast
from pyoload import annotable
from pyoload import annotate
from pyoload import annotate_class
from pyoload import is_annotable
from pyoload import is_annoted
from pyoload import resove_annotations
from pyoload import type_match
from pyoload import unannotable
from pyoload import unannotate

assert pyoload.__version__ == "2.0.1"


@annotate
def foo(a, b=3, c: str = "R") -> Cast(int):
    assert b == 3
    assert isinstance(c, str)
    return '3'


def foo1(a: Cast(str)) -> None:
    return a


@annotate_class(False)
class MyCLass:
    __slots__ = ('a', 'b')
    a: 'int'
    b: 'str'


def test_annotate():
    assert foo(2) == 3
    assert annotate(foo1)(3) == "3"
    assert unannotate(annotate(foo1))(3) == 3
    assert annotate(unannotable(foo1))(3) == 3
    assert annotate(True)(unannotable(foo1))(3) == "3"
    assert annotate(unannotable(foo1), force=True)(3) == "3"
    assert annotate(annotable(unannotable(foo1)))(3) == "3"
    assert is_annotable(foo1)
    assert is_annotable(annotable(foo1))
    assert is_annotable(annotable(unannotable(foo1)))
    assert not is_annotable(unannotable(foo1))
    assert is_annoted(annotate(foo1, force=True))
    assert not is_annoted(foo1)
    annotate(annotate(annotable(foo1)))
    annotate(3)
    try:
        annotate(True)(foo1)(1, 2, 3, 4, 5)
    except Exception:
        pass
    else:
        raise Exception()

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
        @annotate
        def footy() -> 'int':
            pass

        footy()
    except AnnotationError:
        pass
    try:
        type_match(3, any)
    except TypeError:
        pass
    else:
        raise Exception()
    type_match(3, int | tuple[int])
    assert type_match((1, 2), tuple[int, int])[0]
    assert not type_match((1, 3.0), tuple[int, int])[0]
    assert type_match((1, "st"), tuple[int, str])[0]
    assert not type_match((3, 4, 5.0), tuple[int])[0]
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

    assert type_match(3, dict[str | int])
    assert type_match({3: '4'}, dict[int, int])
    assert type_match({'3': 4}, dict[int, int])
    assert type_match((3, 4.0), tuple[int, float])
    assert type_match((3, 4.0), int | tuple[int, float])[0]
    assert not type_match((" 3", 4.0), int | tuple[int, float])[0]


if __name__ == "__main__":
    test_annotate()
