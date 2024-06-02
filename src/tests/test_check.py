import pyoload

from pyoload import AnnotationError
from pyoload import Any
from pyoload import CheckedAttr
from pyoload import Checks
from pyoload import annotate

assert pyoload.__version__ == '1.1.1'


@annotate
class foo:
    foo = CheckedAttr(len=(3, None))
    bar: Checks(ge=3)

    def __init__(self: Any, bar: Checks(func=bool)) -> Any:
        pass


def test_check():
    try:
        foo(0)
    except AnnotationError:
        pass
    else:
        raise Exception()

    obj = foo(2)
    obj.bar = 3
    try:
        obj.bar = 2.9
    except AnnotationError:
        pass
    else:
        raise Exception()


if __name__ == '__main__':
    test_check()
