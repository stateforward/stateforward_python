from stateforward.model.visitor import Visitor


__all__ = ("Preprocessor",)


class Preprocessor(Visitor, visit_method_prefix="preprocess"):
    pass
