import pyoload

from pyoload import *

assert pyoload.__version__ == '1.1.1'


@annotate
class foo:
    foo = CheckedAttr(len=(3, None))
    bar: Checks(ge=3)

    def __init__(self: Any, bar: Checks(func=bool)) -> Any:
        pass


def CheckTest():
    try:
        foo(0)
    except Check.CheckError:
        pass
    else:
        raise Exception()

    obj = foo(2)
    obj.bar = 3
    try:
        obj.bar = 2.9
    except Check.CheckError:
        pass
    else:
        raise Exception()


if __name__ == '__main__':
    CheckTest()
