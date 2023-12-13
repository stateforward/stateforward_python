import stateforward.model as sf


class E0(sf.Element):
    left: sf.Element = None
    right: sf.Element = None


def e0(left: sf.Element = None, right: sf.Element = None):
    return sf.element.new(
        "E0",
        (E0,),
        left=left,
        right=right,
    )


class A(sf.Element):
    a: int

    class B(sf.Element):
        class C(sf.Element):
            pass

    class D(sf.Element):
        pass

    E = sf.collection(B, D)
    F = e0(left=B, right=D)


class B(A):
    pass


print(list(sf.descendants_of(A)))
sf.dump(A)
# sf.dump(B)

# b = B()
