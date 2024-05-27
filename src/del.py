from pyoload import *
import pyoload

assert pyoload.__version__ == '1.1.0'


@annotate
class foo:
    fa: 'str'

    def __init__(self: 'foo', bar: Cast(dict[int, list[float]])):
        self.foo = bar
        assert typeMatch(bar, dict[int, list[float]])


b = foo({'1': ['1.0', 3]})


@annotate
def cassy(v:Checks(ge=3), v1:Checks(gt=4)) -> Checks(len=3):
    return 1, 2, 3

cassy(7, 4.1)


"""
mentor-no = 694190032
"""

from pyoload import *
from pathlib import Path


@overload
def div(a: float|int, b: Checks(eq=0)):
    raise ZeroDivisionError()


@overload
def div(a: int, b: int) -> int:
    return a // b


@overload
def div(a: float, b: float) -> float:
    return a / b


@overload
def div(a: Any, b: Any):
    raise NotImplementedError()


print(div.__pyo_overloads__)
print(div.__pyod_overloads_name__)

print(repr(div(1, 2)))
print(repr(div(1.0, 2.0)))
print(repr(div(1.0, 2)))
print(repr(div('0', 0)))
print(repr(div('0', 1j)))
