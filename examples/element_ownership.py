import stateforward as sf


class A(sf.Element):
    b = sf.new_element("b")

    class B(sf.Element):
        pass

    c = sf.collection(
        B, b
    )  # here the collection takes a weak ownership of both B and b because they aren't defined in a namespace
