import pyoload

from pyoload import Checks
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


def test_overload():
    #assert div("4", "2") == "2.0"
    #assert div(..., 0) == "Infinity"
    assert div("4", 2) == 2
    #assert div(3.0, 1.0) == 3.0


if __name__ == "__main__":
    test_overload()
