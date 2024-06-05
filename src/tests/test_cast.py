import pyoload

from pyoload import Any
from pyoload import Cast
from pyoload import CastedAttr
from pyoload import annotate
from pyoload import typeMatch
from pyoload import AnnotationError
from pyoload import Union

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
    assert typeMatch(q.foo, dict[str, tuple[Union[int, str]]])
    assert typeMatch(q.bar, list[tuple[float]])


if __name__ == "__main__":
    test_cast()
