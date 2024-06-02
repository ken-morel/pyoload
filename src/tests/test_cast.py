import pyoload

from pyoload import Any
from pyoload import Cast
from pyoload import CastedAttr
from pyoload import annotate
from pyoload import typeMatch

assert pyoload.__version__ == '1.1.2'


@annotate
class foo:
    foo = CastedAttr(dict[str, tuple[int | str]])
    bar: Cast(list[tuple[float]])

    def __init__(self: Any, bar: list) -> Any:
        self.bar = bar


def test_cast():
    q = foo([(1, '67')])
    q.foo = {1234: {'5', 16j}}
    assert typeMatch(q.foo, dict[str, tuple[int | str]])
    assert typeMatch(q.bar, list[tuple[float]])


if __name__ == '__main__':
    test_cast()
