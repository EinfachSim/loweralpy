class SyntaxError(Exception):
    "Raised when there is some error in the Syntax"
    pass
class NotInMemoryError(Exception):
    "Raised when there is a var or constant or memload that is not initialised"
    pass
class LASMRuntimeError(Exception):
    "Raised when there is a generic error during emulation"
    pass