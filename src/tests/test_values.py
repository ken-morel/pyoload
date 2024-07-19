from pyoload import annotate
from pyoload import Values
from pyoload import AnnotationError
import pyoload


assert pyoload.__version__ == "2.0.2"


@annotate
def odd(a: Values(range(10))) -> bool:
    return a % 2 == 1


def test_values():
    assert odd(3), "3 reported not odd"
    assert not odd(2), "2 reported odd"

    try:
        odd(10)
    except AnnotationError:
        pass
    else:
        raise AssertionError("Values did not crash")
