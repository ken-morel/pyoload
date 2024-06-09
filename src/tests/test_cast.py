import pyoload

from pyoload import AnnotationError
from pyoload import Any
from pyoload import Cast
from pyoload import CastedAttr
from pyoload import CastingError
from pyoload import Union
from pyoload import annotate
from pyoload import type_match

assert pyoload.__version__ == "2.0.0"


@annotate
class foo:
    foo = CastedAttr(dict[str, tuple[Union[int, str]]])
    bar: Cast(list[tuple[float]])
    a: "str"

    def __init__(self: "Any", bar: "list") -> Any:
        self.bar = bar
        self.a = "ama"
        try:
            self.a = 3
        except AnnotationError:
            pass
        else:
            pass


def test_cast():
    q = foo([(1, "67")])
    q.foo = {1234: {"5", 16j}}
    assert type_match(q.foo, dict[str, tuple[Union[int, str]]])
    assert type_match(q.bar, list[tuple[float]])
    assert Cast(dict[int])({'3': '7'}) == {3: '7'}
    assert Cast(dict[Any, int])({'3': '7'}) == {'3': 7}
    assert Cast(tuple[int | str])(('3', 2.5, 1j, '/6')) == (3, 2, '1j', '/6')

    try:
        @annotate
        def foo2(a: 'Cast(None)'):
            pass
        foo2(3)
    except Exception:
        pass
    else:
        raise Exception()

    try:
        Cast(int | float)(1j)
    except CastingError:
        pass
    else:
        raise Exception()

if __name__ == "__main__":
    test_cast()
