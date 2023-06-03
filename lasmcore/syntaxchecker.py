from lasmcore.exceptions import *
from lasmcore.instructions import *
class SyntaxChecker:
    def __init__(self, debug=False):
        self.line = None
        self.linenumber = -1
        self.debug = debug
        self.debugMessage = ""
        self.label_dict = {}
    def check_syntax(self, line, linenumber):
        self.line = line
        self.linenumber = linenumber+1
        #If line starts with something other than a char, immediately fail
        self.check_alpha(line)
        """LABELS"""
        first_double_point = line.find(":")
        if len(line) == first_double_point+1:
            label_name = line[:first_double_point].strip()
            if not self.is_addr_or_label(label_name):
                self.debugMessage = "Compilation failed because an invalid label name was encountered."
                self.fail()
            self.label_dict[label_name] = linenumber
            return NoOp()
        if first_double_point != -1 and line[:first_double_point].strip().isalpha() and line[first_double_point+1] != "=":
            self.label_dict[line[:first_double_point].strip()] = linenumber
            line = line[first_double_point+1:].strip()
            #Check first char alpha again, because we changed the line
            self.check_alpha(line)
        """EMPTY LINE"""
        if line == "":
            return NoOp()
        """GOTO"""
        if line[:4] == "goto":
            goto_addr = line[5:].strip()
            if not self.is_addr_or_label(goto_addr):
                self.debugMessage = "Compilation failed because an invalid jump_address was encountered."
            return Jump(goto_addr)
        """STACK OPERATIONS"""
        if line == "pop":
            return StackPop()
        if line[:4] == "push":
            push_element = self.check_alnum_or_memload(line[5:].strip())
            if push_element == -1:
                self.debugMessage = "Compilation failed because of an invalid variable name in the push operation"
                self.fail()
            return StackPush(push_element)
        """CONDITIONAL JUMPS"""
        if line[0:2] == "if":
            #Check if " then goto " is in the line and immediately fail if not
            if " then goto " not in line:
                if self.debug:
                    self.debugMessage = "Compilation failed because ' then goto ' could not be found or is ill-formatted or the jump label is missing."
                self.fail()
            #Check if the jump label is valid (only alphabetical)
            label_begin = line.index("then") + len("then goto ")
            if not self.is_addr_or_label(line[label_begin:]):
                self.debugMessage = f"Compilation failed because the label '{line[label_begin:]}' is not alphabetical."
                self.fail()
            jump_label = line[label_begin:]
            #Get the bool expression and parse it
            expr_begin = 3 #Get the index of the bool expression
            expr_stop = line.index("then") #Get the index of "then"
            expr = line[expr_begin:expr_stop].strip()
            jump_condition = self.validate_bool_expression(expr)
            return ConditionalJump(jump_condition, jump_label)
        """DECLARATIONS"""
        if ":=" in line:
            assignment_index = line.find(":=")
            target_location = self.check_alnum_or_memload(line[:assignment_index].strip())
            if target_location == -1:
                self.debugMessage = "Compilation failed because an invalid variable name as destination was encountered"
                self.fail()
            value = line[assignment_index+2:].strip()
            expr = self.validate_algebraic_expression(value)
            #If expr is only a var, const or memload
            if len(expr) == 1:
                return LoadFrom(target_location, expr[0])
            #Else
            return EvalAndLoad(target_location, expr)
        """CALL AND RETURN"""
        if line == "return":
            return Return()
        if line[:4] == "call":
            label_name = line[4:].strip()
            #If the label name contains non-alphabetical chars, fail immediately
            if not label_name.isalpha():
                self.debugMessage = "Compilation failed because the call_label is invalid"
                self.fail()
            return Call(linenumber, label_name)
        #If none of the previous patterns matched, fail because we dont know the instruction
        self.debugMessage = "Compilation failed because an unknown instruction was encountered."
        self.fail()
       
    #If smth does not start with an alphabetic char, fail immediately
    def check_alpha(self, string):
        if string != "" and not string[0].isalpha():
            if self.debug:
                self.debugMessage = "Compilation failed because the first character in the instruction is not alphabetical."
            self.fail()
    #If smth does not start with an alphanumeric char, fail immediately
    def check_alphanumeric(self, string):
        if string != "" and not string[0].isalnum():
            if self.debug:
                self.debugMessage = "Compilation failed because the first character in the instruction is not alphanumerical."
            self.fail()
    #Custom alnum method to validate varnames, constants and memory loads
    def check_alnum_or_memload(self, string):
        #If its a memory load
        operand = string
        if string[:2] == "r(":
            load_end_index = string.index(")")
            operand = string[2:load_end_index]
            if len(string) != load_end_index+1:
                return -1
            if not operand.isalpha():
                self.debugMessage = "Compilation failed because the var_name in the MemLoad contains non-alphabetical chars."
                self.fail()
            return MemLoad(operand)
        #If it is not a memload
        if not operand.isalnum():
            self.debugMessage = "Compilation failed because some var_name contains non-alphanumerical chars."
            return -1
        
        return string
    def is_addr_or_label(self, addr):
        try:
            int(addr)
            return True
        except:
            if addr.isalpha():
                return True
        return False

    #Validate bool expressions encountered in if statements.
    #These can take on the form of x op y, where op is any valid comparator.
    def validate_bool_expression(self, expr):
        #Check if the expr starts with an alphanumerical value
        self.check_alphanumeric(expr)
        #Valid comparators
        ops = ["<=", ">=", "!=", "<", ">", "="]
        #Get the first comparator to match
        comparator_index = None
        comparator = None
        for op in ops:
            index = expr.find(op)
            if index > 0:
                comparator_index = index
                comparator = op
                break
        if comparator_index == None or comparator == None:
            if self.debug:
                self.debugMessage = "Compilation failed because the comparator matching did not succeed."
            self.fail()
        operand1 = expr[:comparator_index].strip()
        operand2 = expr[comparator_index+len(op):].strip()
        #Check if both operands are alphanumerical values or memory loads
        op1_check = self.check_alnum_or_memload(operand1)
        op2_check = self.check_alnum_or_memload(operand2)
        if op1_check == -1 or op2_check == -1:
            self.debugMessage = "Compilation failed because the bool operands are invalid"
            self.fail()
        return [op1_check, comparator, op2_check]
    def validate_algebraic_expression(self, expr):
        #Check if it even is an expression or if it is just a variable name, constant or memory load
        expr_check = self.check_alnum_or_memload(expr)
        if expr_check != -1:
            return [expr_check]
        #Check if the expr starts with an alphanumerical value
        self.check_alphanumeric(expr)
        #Valid operators
        ops = ["+", "-", "*", "/", "%"]
        #Get the first operator to match
        operator_index = None
        operator = None
        for op in ops:
            index = expr.find(op)
            if index > 0:
                operator_index = index
                operator = op
                break
        if operator_index == None or operator == None:
            if self.debug:
                self.debugMessage = "Compilation failed because the operator matching did not succeed."
            self.fail()
        operand1 = expr[:operator_index].strip()
        operand2 = expr[operator_index+len(op):].strip()
        #Check if both operands are alphanumerical values or memory loads
        op1_check = self.check_alnum_or_memload(operand1)
        op2_check = self.check_alnum_or_memload(operand2)
        if op1_check == -1 or op2_check == -1:
            self.debugMessage = "Compilation failed because the algebraic operands are invalid"
            self.fail()
        return [op1_check, operator, op2_check]

    """
    Fail safely when the syntax check does not work
    """
    def fail(self):
        print()
        print(self.line)
        if self.debug:
            print(self.debugMessage)
        raise SyntaxError("SyntaxError at line " + str(self.linenumber) + "!")