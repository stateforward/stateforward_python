class A:
    def __init_subclass__(cls, **kwargs):
        print("A.__init_subclass__", cls, kwargs)


class B(A):
    def __init_subclass__(cls, **kwargs):
        print("B.__init_subclass__", cls, kwargs)
        super().__init_subclass__(**kwargs)


class C(B, foo="bar", baz="qux"):
    pass
