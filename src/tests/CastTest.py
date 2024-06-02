import pyoload

from pyoload import *

assert pyoload.__version__ == '1.1.1'


@annotate
class foo:
    foo = CastedAttr(dict[str, tuple[int | str]])
    bar: Cast(list[tuple[float]])

    def __init__(self: Any, bar: list) -> Any:
        self.bar = bar


def CastTest():
    q = foo()
    q.foo = {1234: {'5', 16j}}
    assert typeMatch(q.foo, dict[str, tuple[int | str]])
    assert typeMatch(q.bar, list[tuple[float]])


if __name__ == '__main__':
    CastTest()
