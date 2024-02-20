from abc import ABC, abstractmethod
from common.exceptions import *
from common.token_enums import *
from xml.etree import ElementTree as ET
import sys

from lexer.token import Token

class OperandsContext():
    def __init__(self, operands_context) -> None:
        self.operands_context = operands_context

    def check(self, operands):
        """
        Checks, whether a given operand list matches this context
        """

    def _operands_compare(self,operands_a, operands_b):
        if len(operands_a) != len(operands_b):
            return False
        
        for operand_a,operand_b in zip(operands_a,operands_b):
            if operand_a == TokenTypes.SYM and operand_b in [TokenTypes.INT, TokenTypes.STR, TokenTypes.NIL, TokenTypes.VAR, TokenTypes.BOOL]:
                continue
            if operand_b == TokenTypes.SYM and operand_a in [TokenTypes.INT, TokenTypes.STR, TokenTypes.NIL, TokenTypes.VAR, TokenTypes.BOOL]:
                continue
            if operand_a == operand_b:
                continue
            return False
        return True


class State(ABC):
    endingState = False

    def __init__(self, context) -> None:
        self.context = context

    @abstractmethod
    def handle(self) -> object:
        pass

class StateHeader(State):
    def handle(self):
        """
        Checks the compulsory occurence of the .IPPcode24 header
        Raises MissingHeadError if the header is not properly placed/missing
        """
        if not self.context.next_token_buffer():
            # end of token stream
            print(self.context.token_buffer)
            raise MissingHeadError

        if len(self.context.token_buffer) != 1 or self.context.token_buffer[0].type != TokenTypes.HEAD:
            # header is not alone on the line or it is missing
            print(self.context.token_buffer)
            raise MissingHeadError
        else:
            return StateInstrSetContext(self.context)

class StateInstrSetContext(State):
    def _operands_compare(self,operands_a, operands_b):
        if len(operands_a) != len(operands_b):
            return False
        
        for operand_a,operand_b in zip(operands_a,operands_b):
            if operand_a == TokenTypes.SYM and operand_b in [TokenTypes.INT, TokenTypes.STR, TokenTypes.NIL, TokenTypes.VAR, TokenTypes.BOOL]:
                continue
            if operand_b == TokenTypes.SYM and operand_a in [TokenTypes.INT, TokenTypes.STR, TokenTypes.NIL, TokenTypes.VAR, TokenTypes.BOOL]:
                continue
            if operand_a == operand_b:
                continue
            return False
        return True

    def _get_operand_context(self,opcode : str, operands : list):
        """
        Accepts instruction opcode and its argument types given by lexer
        Returns argument types according to their context (instruction they are used in) or None if the operand
        """

        symb = [TokenTypes.VAR, TokenTypes.INT, TokenTypes.STR, TokenTypes.BOOL, TokenTypes.NIL]
        operand_types = [operand.type for operand in operands]

        if opcode in ("MOVE", "STRLEN", "TYPE", "NOT", "INT2CHAR"):
            # operands: VAR SYMB
            if self._operands_compare(operand_types, [TokenTypes.VAR, TokenTypes.SYM]):
                return True, operand_types
        if opcode in ("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN"):
            # no operands
            if self._operands_compare(operand_types, []):
                return True, operand_types
        if opcode in ("PUSHS", "WRITE", "EXIT"):
            # operands: SYMB
            if self._operands_compare(operand_types, [TokenTypes.SYM]):
                return True, operand_types
        if opcode in ("DEFVAR", "POPS"):
            # operands: VAR
            if self._operands_compare(operand_types, [TokenTypes.VAR]):
                return True, operand_types
        if opcode in ("ADD", "SUB", "MUL", "IDIV","LT", "GT", "EQ",
                      "AND", "OR", "STR2INT", "CONCAT", "GETCHAR",
                      "SETCHAR", ):
            # operands: VAR SYMB SYMB
            if self._operands_compare(operand_types, [TokenTypes.VAR, TokenTypes.SYM, TokenTypes.SYM]):
                return True, operand_types
        if opcode in ("READ"):
            # operands: VAR TYPE
            if self._operands_compare(operand_types, [TokenTypes.VAR, TokenTypes.ALPHANUM]) and operands[1].string in ['int', 'bool', 'string']:
                return True, [TokenTypes.VAR, TokenTypes.TYPE]
        if opcode in ("LABEL", "CALL", "JUMP"):
            # operands: LABEL
            if self._operands_compare(operand_types, [TokenTypes.ALPHANUM]):
                return True, [TokenTypes.LABEL]
        if opcode in ("JUMPIFEQ", "JUMPIFNEQ"):
            # operands: LABEL SYMB SYMB
            if self._operands_compare(operand_types, [TokenTypes.ALPHANUM, TokenTypes.SYM, TokenTypes.SYM]):
                return True, [TokenTypes.LABEL, operand_types[1], operand_types[2]]

        return False, None
    

    def handle(self):
        """
        Reads one line of tokens and changes their types based on the context (detected instruction opcode).
        Raises OpcodeError exception if the opcode cannot be determined.
        Raises SyntaxError exception if the arguments cannot be transformed based on the context
        """
        if not self.context.next_token_buffer():
            # end of token stream
            return StateFinish(self.context)

        opcode = self.context.token_buffer[0].string.upper()
        operands = self.context.token_buffer[1:]

        opcode_correct, arguments_context = self._get_operand_context(opcode,operands)

        if not opcode_correct:
            raise OpcodeError
        elif arguments_context == None:
            raise SyntaxError

        # change the first token type to instruction type
        self.context.token_buffer[0].type = TokenTypes.INST
        # change the argument token types 
        for idx in range(0, len(arguments_context)):
            # the tokens to be modified start on index 1, the token on index 0 is the opcode
            self.context.token_buffer[idx+1].type = arguments_context[idx]

        return StateInstrBuild(self.context)

class StateInstrBuild(State):
    def _format_operand_string(self, operand):
        """
        Edit the token str for printing into the output XML tree
        Returns the formatted token string
        """
        if operand.type in [TokenTypes.INT, TokenTypes.BOOL, TokenTypes.STR, TokenTypes.NIL]:
            return operand.string.split('@',1)[1]

        # other types remain unchanged
        return operand.string



    def handle(self):
        """
        Appends the instruction to the output XML tree
        """
        instr_el = ET.SubElement(self.context.output_root, 'instruction')
        instr_el.set("order", str(self.context.instruction_cnter))
        instr_el.set("opcode", self.context.token_buffer[0].string.upper())
        
        operands = self.context.token_buffer[1:]
        for idx, operand in enumerate(operands):
            operand_el = ET.SubElement(instr_el, "arg" + str(idx+1))
            operand_el.set("type", operand.type.value)
            operand_el.text = self._format_operand_string(operand)

        self.context.instruction_cnter += 1
        return StateInstrSetContext(self.context)

class StateFinish(State):
    endingState = True
    def handle(self):
        """
        Dumps the element tree in stdout
        """
        output_tree = ET.ElementTree(self.context.output_root)
        ET.indent(output_tree, space="\t", level=0)
        output_tree.write(sys.stdout.buffer, encoding="utf-8", xml_declaration=True)
