import sys
import lasmcore.main as lsc
from lasmcore.exceptions import *
if __name__ == "__main__":
    try:  
        file = sys.argv[1]
        with open(file) as f:
            lines = f.readlines()
            lsc.assemble(lines)
    except FileNotFoundError:
        print("The specified file does not exist!")
    except SyntaxError as e:
        print(e)
    except NotInMemoryError as e:
        print(e)
    except LASMRuntimeError as e:
        print(e)