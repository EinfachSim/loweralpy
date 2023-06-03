from lasmcore.syntaxchecker import SyntaxChecker
from lasmcore.emulation.lasm_emulator import Interpreter
def assemble(lines):
    sc = SyntaxChecker(debug=True)
    program = []
    for linenum, line in enumerate(lines):
        line = line.strip()  
        inst = sc.check_syntax(line, linenum)
        program.append(inst)
    emulator = Interpreter(debug=True)
    print(sc.label_dict)
    emulator.emulate(program, sc.label_dict)
