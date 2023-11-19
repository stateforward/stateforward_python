from stateforward.model.visitor import Visitor


class Validator(Visitor, visit_method_prefix="validate"):
    pass
