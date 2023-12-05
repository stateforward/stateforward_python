import stateforward as sf
from typing import Union


class FamilyTreeElement(sf.Element):
    def __new__(cls, *args, **kwargs):
        print(f"{cls.qualified_name}.__new__")
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        print(f"{self.qualified_name}.__init__")
        super().__init__(*args, **kwargs)


class Person(FamilyTreeElement):
    first_name: str
    age: int
    kids: Union[FamilyTreeElement, sf.Collection[FamilyTreeElement]] = None
    spouse: FamilyTreeElement = None

class FamilyTree(FamilyTreeElement):
    pass


class Family(FamilyTree):
    class Dad(Person, first_name="John", age=40):
        pass

    class Mom(Person, first_name="Jane", age=38):
        class Son(Person, first_name="Jack", age=15):
            pass

        class Daughter(Person, first_name="Jill", age=26):
            class Grandson(Person, first_name="Jimmy", age=1):
                pass

            class Granddaughter(Person, first_name="Jenny", age=3):
                pass

        class SonInLaw(
            Person,
            first_name="John",
            age=26,
            kids=sf.collection(Daughter.Grandson, Daughter.Granddaughter),
            spouse=Daughter,
        ):
            pass

    non_blood_related: FamilyTree = Mom.SonInLaw

class Cousin(Person, first_name="Joe", age=20):
    adopted_family: FamilyTree = None

def element_example_main():
    redefined_family = sf.redefine(Family)
    sf.dump(redefined_family)
    print(redefined_family.attributes)
    new_family = sf.new_element(
        "NewFamily", (Cousin,), adopted_family=redefined_family, attributes=redefined_family.attributes
    )
    print(new_family.Dad)


element_example_main()