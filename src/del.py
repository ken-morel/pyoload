from pyoload import *
import pyoload

assert pyoload.__version__ == '1.1.0'


@annotate
class foo:
    fa: 'str'

    def __init__(self: 'foo', bar: Cast(dict[int, list[float]])):
        self.foo = bar


b = foo({'1': ['1.0', 3]})


@annotate
def ca(v=Checks(ge=3)) -> Checks(len=3):
    print(dkdkdjd)
    return 1, 2, 3


ca(5)


"""
mentor-no = 694190032
"""
