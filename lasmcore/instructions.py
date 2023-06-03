class ConditionalJump:
    def __init__(self, parsed_condition, jump_label):
        self.parsed_condition_list = parsed_condition
        self.jump_label = jump_label
    def __str__(self):
        return "ConditionalJump Instruction: {condition: " + str("".join([str(cond) for cond in self.parsed_condition_list])) + ", jump_label: " + str(self.jump_label) + "}"
class StackPop:
    def __str__(self):
        return "StackPop Instruction"
class StackPush:
    def __init__(self, element):
        self.element = element
    def __str__(self):
        return "StackPush Instruction: {element: " + str(self.element) + "}"
class LoadFrom:
    def __init__(self, dest, src):
        self.dest = dest
        self.src = src
    def __str__(self):
        return "LoadFrom Instruction: {destination: " + str(self.dest) + ", from: " + str(self.src) + "}"
class EvalAndLoad:
    def __init__(self, dest, src_expr):
        self.dest = dest
        self.src_expr = src_expr
    def __str__(self):
        return "EvalAndLoad Instruction: {destination: " + str(self.dest) + ", from_expression: " + str("".join([str(cond) for cond in self.src_expr])) + "}"
class Return:
    def __str__(self):
        return "Return Instruction"
class Call:
    def __init__(self, return_addr, call_label):
        self.return_addr = return_addr
        self.call_label = call_label
    def __str__(self):
        return "Call Instruction: {return_addr: " + str(self.return_addr) + ", call_label: " + str(self.call_label) + "}"
class NoOp:
    def __str__(self):
        return "NoOp"
class Jump:
    def __init__(self, jump_label):
        self.jump_label = jump_label
    def __str__(self):
        return "Jump Instruction: {jump_adress: " + str(self.jump_label) + "}"
#Pseudoinstruction
class MemLoad:
    def __init__(self, src):
        self.src = src
    def __str__(self):
        return "MemLoad(" + str(self.src) + ")"