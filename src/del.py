from pyoload import *
import pyoload

assert pyoload.__version__ == '1.1.1'


@annotate
class foo:
    foo = CastedAttr(dict[str, tuple[int | str]])

    def __init__(self: Any) -> Any:
        pass


q = foo()
q.foo = {1234: {'5', 16j}}
