import pyoload

from pyoload import AnnotationError
from pyoload import Any
from pyoload import CheckedAttr
from pyoload import Checks
from pyoload import Check
from pyoload import annotate

assert pyoload.__version__ == "2.0.0"


@annotate
class foo:
    foo = CheckedAttr(len=(3, None))
    bar: Checks(ge=3)

    def __init__(self: Any, bar: Checks(func=bool)) -> Any:
        pass


@Check.register("test1 test2")
def __(param, val):
    print(param, val)


class IsInt(Check):
    name = "isint"

    def __call__(self, a, b):
        return a == isinstance(b, int)


def test_check():
    try:
        foo(0)
    except AnnotationError:
        pass
    else:
        raise Exception()

    obj = foo(2)
    obj.bar = 3
    try:
        obj.bar = 2.9
    except AnnotationError:
        pass
    else:
        raise Exception()

    Checks(bool)(1)
    try:
        Checks(bool)(0)
    except Exception:
        pass
    else:
        raise Exception()
    try:
        Checks(len=3)(0)
    except Exception:
        pass
    else:
        raise Exception()
    try:
        Checks(len=3)((0,))
    except Exception:
        pass
    else:
        raise Exception()
    try:
        Checks(len=slice(3, None))((0,))
    except Exception:
        Checks(len=slice(3, None))((0, 1, 2))
    else:
        raise Exception()
    try:
        Checks(len=slice(3))((0, 1, 2))
    except Exception:
        Checks(len=slice(3))((0, 1))
    else:
        raise Exception()
    Checks(test1=3)(3)
    Checks(test2=4)(4)
    Checks(ge=2, gt=1, lt=2.1, le=2, eq=2)(2)
    print(Checks(ge=-2.5, gt=-3, lt=-2, le=2, eq=-2.5)(-2.5))
    Checks(len=slice(2, 5))("abcd")
    Checks(type=dict[str | int, tuple[int]])(
        {
            "#": (12,),
            20: (21, 45),
        }
    )
    Checks(isinstance=float)(1.5)
    Checks(isint=True)(5)

    for name, check in pyoload.Check.checks_list.items():
        try:
            if pyoload.get_name(check).split(".")[0] == "tests":
                continue
            pyoload.Checks(**{name: NotImplemented})(24)
        except pyoload.Check.CheckError:
            pass
        else:
            raise Exception(name, check)
        try:
            if pyoload.get_name(check).split(".")[0] == "tests":
                continue
            pyoload.Checks(**{name: int})(11)
        except pyoload.Check.CheckError:
            if name in ('func', 'type'):
                raise Exception()
        else:
            if name not in ('func', 'type'):
                raise Exception(name, check)
        try:
            if pyoload.get_name(check).split(".")[0] == "tests":
                continue
            pyoload.Checks(**{name: 3})(11)
        except pyoload.Check.CheckError:
            if name in ('ge', 'gt'):
                raise Exception()
        else:
            if name not in ('ge', 'gt'):
                raise Exception(name, check)
    pyoload.Checks(len=3)((1, 2, 3))
    pyoload.Checks(len=2)((1, 2))
    pyoload.Checks(len=slice(3, None))((1, 2, 3))
    pyoload.Checks(len=slice(3))((1, 2))


if __name__ == "__main__":
    test_check()
