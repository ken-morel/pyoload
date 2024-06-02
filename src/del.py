from pyoload import annotate, Cast, Checks, typeMatch, resolveAnnotations, Any
import pyoload

assert pyoload.__version__ == '1.1.1'


@annotate
class foo:
    foo: dict[int, list[float]]

    def __init__(self: 'foo', bar: Cast(dict[int, list[float]])):
        self.foo = bar

    def gama(self: Any, b: str):
        return len(b)

print(foo.gama.__annotations__)
resolveAnnotations(foo.gama)
print(foo.gama.__annotations__)
b = foo({'1': ['1.0', 3]})
print(foo.__init__.__annotations__)
b.gama('ama')

print(b.foo)
