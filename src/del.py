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
