import pyoload

from pyoload import Checks
from pyoload import OverloadError
from pyoload import get_name
from pyoload import overload

assert pyoload.__version__ == "2.0.0"


@overload
def div(a: str, b: Checks(eq=0)):
    return "Infinity"


@overload(get_name(div))
def div_(a: str, b: str):
    print(f"{a=}, {b=} -> str")
    return str(float(a) / float(b))


@div_.overload
def div___(a: str, b: int):
    print(f"{a=}, {b=} -> int")
    return int(float(a) / b)


@div.overload
def div____(a: float, b: float):
    print(f"{a=}, {b=} -> float")
    return float(float(a) / b)


@overload
def foo(a) -> int:
    return 1


@overload
def foo(a, b) -> int:
    return 2


@overload
def foo(a, b, c) -> int:
    return 3


def test_overload():
    assert div("4", "2") == "2.0"
    try:
        assert div(..., 0) == "Infinity"
    except OverloadError:
        pass
    else:
        raise Exception()
    assert div("4", 2) == 2
    assert div(3.0, 1.0) == 3.0

    assert foo(1) == 1
    assert foo(1, 2) == 2
    assert foo(1, 2, 3) == 3


if __name__ == "__main__":
    test_overload()
