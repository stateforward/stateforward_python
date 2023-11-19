import stateforward as sf


class ColorWheelValidator(sf.Validator):
    def validate_color_wheel(self, element: type["ColorWheel"]):
        print(f"validate_color_wheel({element.name})")
        self.validate_owned_elements(element)

    def validate_red(self, element: type["Theme.Red"]):
        print("validate_red(Red)")
        self.validate_color(element, 2)  # must call this to validate the color

    def validate_green(self, element: type["Theme.Green"]):
        print("validate_green(Green)")

    def validate_color(self, element: type["Color"], indent=0):
        print(f"{' ' * indent}validate_color({element.name})")


class Color(sf.Element):
    pass


class ColorWheel(sf.Model, validator=ColorWheelValidator()):
    pass


class Theme(ColorWheel):
    class Red(Color):
        pass

    class Green(Color):
        pass

    class Blue(Color):
        pass
