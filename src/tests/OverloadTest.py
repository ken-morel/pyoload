import pyoload

from pyoload import *

assert pyoload.__version__ == '1.1.1'


@overload
def div(a: str, b: str):
    return str(float(a) / float(b))


@overload(get_name(div))
def div_(a: str, b: Checks(eq=0)):
    return 'Infinity'


@overload(get_name(div))
def div__(a: Any, b: Checks(eq=0)):
    return NotImplemented


@div_.overload
def div___(a: str, b: int):
    return int(float(a) / b)


@div.overload
def div____(a: float, b: float):
    return float(float(a) / b)


def OverloadTest():
    assert div('4', '2') == '2.0'
    assert div('3', 0) == 'Infinity'
    assert div(None, 0) == NotImplemented
    assert div("4", 2) == 2
    assert div(3.0, 1.0) == 3.0


if __name__ == '__main__':
    OverloadTest()
