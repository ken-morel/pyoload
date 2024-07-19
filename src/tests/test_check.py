import pyoload

from pyoload import AnnotationError
from pyoload import Any
from pyoload import CheckedAttr
from pyoload import Checks
from pyoload import Check
from pyoload import annotate

assert pyoload.__version__ == "2.0.2"


@annotate
class foo:
    foo = CheckedAttr(len=slice(3, None))
    foow = CheckedAttr(len=slice(3, None))
    bar: Checks(ge=3)

    def __init__(self: Any, bar: Checks(bool)) -> Any:
        pass


@Check.register("test1 test2")
def __(param, val):
    print(param, val)


class IsInt(Check):
    name = "isint"

    def __call__(self, a, b):
        assert a == isinstance(b, int)


def test_check():
    try:
        foo(0)
    except AnnotationError:
        pass
    else:
        raise Exception()

    obj = foo(2)
    obj.bar = 3
    obj.foo = ('1', 2, 3)
    Check.check("_isint", True, None)
    try:
        obj.foow = None
    except Exception:
        pass
    else:
        raise Exception()
    try:
        obj.foo = ('1', 2)
    except Check.CheckError:
        pass
    else:
        raise Exception()

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
    # print(Checks(ge=-2.5, gt=-3, lt=-2, le=2, eq=-2.5)(-2.5))
    Checks(len=slice(2, 5))("abcd")
    Checks(type=dict[str | int, tuple[int]])(
        {
            "#": (12,),
            20: (21, 45),
        }
    )
    Checks(isinstance=float)(1.5)
    Checks(isint=True)(5)
    Checks(_isint=False)(5)
    try:
        Checks(_isint=True)(5)
    except Check.CheckError:
        pass
    else:
        raise Exception("did not fail")

    for name, check in pyoload.Check.checks_list.items():
        try:
            print(pyoload.get_name(check))
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
            if name in ('func', 'type', 'isinstance'):
                raise Exception()
        else:
            if name not in ('func', 'type', 'isinstance'):
                raise Exception(name, check)
        try:
            if pyoload.get_name(check).split(".")[0] == "tests":
                continue
            pyoload.Checks(**{name: 3})(11)
            pyoload.Checks(**{name: 11})(3)
        except pyoload.Check.CheckError:
            pass
        else:
            raise Exception(name, check)
    pyoload.Checks(len=3)((1, 2, 3))
    pyoload.Checks(len=2)((1, 2))
    pyoload.Checks(len=slice(3, None))((1, 2, 3))
    pyoload.Checks(len=slice(3))((1, 2))

    try:
        Checks(type=str)(3)
    except Check.CheckError:
        pass
    try:
        Checks(isinstance=str)(3)
    except Check.CheckError:
        pass


if __name__ == "__main__":
    test_check()
