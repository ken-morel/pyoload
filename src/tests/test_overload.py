import pyoload

from pyoload import Any
from pyoload import Checks
from pyoload import get_name
from pyoload import overload

assert pyoload.__version__ == '1.1.2'


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


def test_overload():
    print(div.__pyod_overloads__, div.__pyod_overloads_name__)
    print(div_.__pyod_overloads__, div_.__pyod_overloads_name__)
    print(div__.__pyod_overloads__, div__.__pyod_overloads_name__)
    print(div___.__pyod_overloads__, div___.__pyod_overloads_name__)
    print(div____.__pyod_overloads__, div____.__pyod_overloads_name__)
    assert div('4', '2') == '2.0'
    assert div('3', 0) == 'Infinity'
    assert div(..., 0) == NotImplemented
    assert div('4', 2) == 2
    assert div(3.0, 1.0) == 3.0


if __name__ == '__main__':
    test_overload()
