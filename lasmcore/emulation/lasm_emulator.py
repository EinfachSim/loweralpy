from lasmcore.instructions import *
from lasmcore.exceptions import NotInMemoryError, LASMRuntimeError
class Interpreter:
    def __init__(self, debug=False):
        self.memory = {}
        self.registers = {"a": "0"}
        self.stack = []
        self.recursion_stack = []
        self.pc = 0
        self.curr_instruction = None
        self.debug = debug
    def alert_fail(self):
        print()
        print(self.curr_instruction)
        print(f"The interpreted emulation failed at line {self.pc+1}. Execution was halted.")
    def emulate(self, program, labels):
        """
        Available Instructions:
        - ConditionalJump
        - StackPop
        - StackPush
        - LoadFrom
        - EvalAndLoad
        - Return
        - Call
        """
        while(self.pc < len(program)):
            print()
            print("PC: " + str(self.pc+1))
            self.curr_instruction = program[self.pc]
            print(self.curr_instruction)
            if isinstance(self.curr_instruction, Jump):
                dest = self.curr_instruction.jump_label
                dest_addr = None
                try:
                    dest_addr = int(dest)
                    self.pc = dest_addr-1
                except:
                    if dest not in labels:
                        self.alert_fail()
                        raise LASMRuntimeError("Unknown label error.")
                    self.pc = labels[dest]
            if isinstance(self.curr_instruction, NoOp):
                self.pc += 1
            if isinstance(self.curr_instruction, ConditionalJump):
                condition = self.curr_instruction.parsed_condition_list
                jump_label = self.curr_instruction.jump_label
                comp = condition[1]
                if comp == "=":
                    comp = "=="
                var1 = self.get_from_memory(condition[0])
                var2 = self.get_from_memory(condition[2])
                result = None
                try:
                    result = eval(var1+comp+var2)
                except:
                    self.alert_fail()
                    raise LASMRuntimeError("The LASM Emulator encountered an error while evaluating a bool eval. If this error occurs, please check the SyntaxChecker, this should NOT happen during emulation!")
                if result:
                    dest_addr = None
                    try:
                        dest_addr = int(jump_label)
                        self.pc = dest_addr-1
                    except:
                        if jump_label not in labels:
                            self.alert_fail()
                            raise LASMRuntimeError("Unknown label error.")
                        self.pc = labels[jump_label]
                else:
                    self.pc += 1
            if isinstance(self.curr_instruction, StackPop):
                if len(self.stack) == 0:
                    self.alert_fail()
                    raise LASMRuntimeError("Cannot pop from empty stack.")
                self.registers["a"] = self.stack.pop()
                self.pc += 1
            if isinstance(self.curr_instruction, StackPush):
                el = self.curr_instruction.element
                element = self.get_from_memory(el)
                self.stack.append(element)
                self.pc += 1
            if isinstance(self.curr_instruction, LoadFrom):
                dest = self.curr_instruction.dest
                src = self.curr_instruction.src
                src_val = None
                src_val = self.get_from_memory(src)
                if isinstance(dest, MemLoad):
                    self.memory[dest.src] = src_val
                else:
                    self.registers[dest] = src_val
                self.pc += 1
            if isinstance(self.curr_instruction, EvalAndLoad):
                dest = self.curr_instruction.dest
                src_expr = self.curr_instruction.src_expr
                #Get src vars and op
                var1 = self.get_from_memory(src_expr[0])
                var2 = self.get_from_memory(src_expr[2])
                op = src_expr[1]
                #Try evaluating
                src_val = None
                try:
                    src_val = int(eval(var1+op+var2))
                except:
                    self.alert_fail()
                    raise LASMRuntimeError("The LASM Emulator encountered an error while evaluating an algebraic eval. If this error occurs, please check the SyntaxChecker, this should NOT happen during emulation!")
                if isinstance(dest, MemLoad):
                    self.memory[dest.src] = str(src_val)
                else:
                    self.registers[dest] = str(src_val)
                self.pc += 1
            if isinstance(self.curr_instruction, Return):
                if len(self.recursion_stack) == 0:
                    self.alert_fail()
                    raise LASMRuntimeError("Empty Recursion stack. THIS SHOULD NOT HAPPEN!")
                return_addr = self.recursion_stack.pop()
                self.pc = return_addr
            if isinstance(self.curr_instruction, Call):
                self.recursion_stack.append(self.pc+1)
                dest = self.curr_instruction.call_label
                if dest not in labels:
                        self.alert_fail()
                        raise LASMRuntimeError("Unknown label error.")
                self.pc = labels[dest]
            if self.debug:
                print("Memory: " + str(self.memory))
                print("Registers: " + str(self.registers))
                print("Stack: " + str(self.stack))
                print("Recursion stack: " + str(self.recursion_stack))
    #Check if v is in memory or in the registers
    def get_from_memory(self, v):
        if isinstance(v, MemLoad):
            if v.src not in self.memory:
                self.alert_fail()
                raise NotInMemoryError("The specified load address cannot be found in memory")
            return self.memory[v.src]
        else:
            #Try parsing to int
            try:
                return str(int(v))
            #If it doesnt work it should be a register adress
            except:
                #If not, fail
                if v not in self.registers:
                    self.alert_fail()
                    raise NotInMemoryError("There is no initialised register with this name")
                #If so, get the corresponding value
                return self.registers[v]