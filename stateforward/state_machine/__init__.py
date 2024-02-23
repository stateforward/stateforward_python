"""

The `__init__` module serves as the entry point for the package. It initializes the package and makes the functions and elements from the submodules `functional` and `elements` available at the package level. This is achieved by importing all the contents from these submodules, which allows the user to access these functions and elements directly without needing to import them individually from their respective submodules. By doing so, it simplifies the import statements required in client code and offers a more convenient interface to work with the components provided by the package.
"""
from .functional import *
from .elements import *
