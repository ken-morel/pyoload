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
def cassy(v=Checks(ge=3), v1=Checks(gt=4)):
    print(dkdkdjd)
    return 1, 2, 3


print(cassy.__annotations__)
print(cassy.__pyod_annotate__.__annotations__)


cassy(7, 3)


"""
mentor-no = 694190032
"""
