


@annotate
def test(a: str, b: 'int') -> Cast(tuple[float | str]):
    print(repr(a), repr(b))
    return (3, '3.0', 1j)


print(repr(test("ama", 23)))
