from pyoload import *
import pyoload

assert pyoload.__version__ == '1.1.1'


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

@annotate
class Person:
    age: int

    def __init__(self: Any, age: int, name: str):
        self.age = age
        self.name = name


djamago = Person(15, 'djamago')

print(djamago.__annotations__)


from pyoload import Cast

caster = Cast(dict[str, list[tuple[float]]]) # a dictionary of names of
                                             # places[str] to a list of their
                                             # (x, y) coordinates
                                             #             [list[tuple[float]]]

raw = {
    4: (
        ['1.5', 10],
        [10, '1.5'],
    )
}
print(caster(raw))

print("-"*20)
from pyoload import *



@Check.register('is_equal')
def isnonecheck(param, value):
    if param != value:
        raise Check.CheckError(f'{param!r} not equal to {value!r}')

@annotate
def foo(bar: Checks(is_equal=3)):
    pass

foo(3)  # param=3 value=3

print(Cast(tuple[int])("678936798"))

class Person:
    age = CheckedAttr(gt=0)
    phone = CastedAttr(tuple[int])

    def __init__(self, age, phone):
        self.age = age
        self.phone = phone

temeze = Person(17, "678936798")

print(temeze.age)  # 17
print(temeze.phone)  # (6, 7, 8, 9, 3, 6, 7, 9, 8)

mballa = Person(0, "123456")
