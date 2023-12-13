import stateforward as sf


class Wheel(sf.Element):
    size: int


class Engine(sf.Element):
    power: int


class AutomobileValidator(sf.Validator):
    def validate_automobile(self, automobile: type["Automobile"]):
        if automobile.engine is None:
            raise ValueError(f"Automobile {sf.name_of(automobile)} must have an engine")
        elif automobile.wheels is None:
            raise ValueError(f"Automobile {sf.name_of(automobile)} must have wheels")


class AutomobilePreprocessor(sf.Preprocessor):
    def preprocess_automobile(self, element: type["Automobile"]):
        sf.set_attribute(
            element,
            "wheels",
            sf.collection(
                *sf.find_owned_elements_of(
                    element, lambda _element: sf.element.is_subtype(_element, Wheel)
                )
            ),
        )
        engine = sf.find_owned_element_of(
            element, lambda _element: sf.element.is_subtype(_element, Engine)
        )
        sf.set_attribute(
            element,
            "engine",
            engine,
        )


class Automobile(
    sf.Model, validator=AutomobileValidator, preprocessor=AutomobilePreprocessor
):
    manufacturer: str = None
    wheels: sf.Collection["Wheel"] = None
    engine: "Engine" = None


class Car(
    Automobile,
    manufacturer="Saturn",
):
    class V8(Engine, power=300):
        pass

    class FrontLeft(Wheel, size=16):
        pass

    class FrontRight(Wheel, size=16):
        pass

    class RearLeft(Wheel, size=16):
        pass

    class RearRight(Wheel, size=16):
        pass


sf.dump(Car)
