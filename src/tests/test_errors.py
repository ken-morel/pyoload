import pyoload


assert pyoload.__version__ == "2.0.2"


errors = (
    pyoload.AnnotationError,
    pyoload.AnnotationErrors,
    pyoload.InternalAnnotationError,
    pyoload.CastingError,
    pyoload.OverloadError,
    pyoload.AnnotationResolutionError,
)


def test_errors():
    for err in errors:
        try:
            raise err()
        except err:
            pass
        except Exception:
            raise
        else:
            raise Exception()

    pyoload.PyoloadAnnotation()
    v = pyoload.Values((1, 2, 3))
    v(2)
    str(v)

    assert pyoload.get_name(test_errors).endswith("test_errors")

    class Custom(pyoload.Check):
        def __call__(self, a, b):
            assert a == b

    @pyoload.annotate
    def foo(a: pyoload.Checks(Custom=3)):
        pass

    try:
        foo(2)
    except pyoload.AnnotationError:
        foo(3)
    else:
        raise Exception()

    try:
        pyoload.Check.register("Custom")
    except pyoload.Check.CheckNameAlreadyExistsError:
        pass
    else:
        raise Exception()

    @pyoload.Check.register("c2 c3")
    def _(a, b):
        assert a == b

    @pyoload.annotate
    def foo(a: pyoload.Checks(c2=3, c3=3)):
        pass

    try:
        foo(2)
    except pyoload.AnnotationErrors:
        foo(3)
    else:
        raise Exception()

    try:

        @pyoload.annotate
        def bar(c: pyoload.Checks(rub=3)):
            raise Exception(c)

        bar(NotImplemented)
    except pyoload.Check.CheckDoesNotExistError:
        pass
