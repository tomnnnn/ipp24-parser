from abc import ABC, abstractmethod
from common.exceptions import *
from common.token_enums import *
from xml.etree import ElementTree as ET
import sys

from lexer.token import Token

class OperandsReference():
    def __init__(self, reference, context_template) -> None:
        self.reference = reference
        # set the template for determining the right token types based on the context (instruction)
        if context_template == None:
            self.context_template = reference
        else:
            self.context_template = context_template

    def compare(self, operands : list[Token]) -> list[TokenTypes]:
        """
        Compares the given operands list with the reference
        """
        # 
        types_context = []

        if len(self.reference) != len(operands):
            raise SyntaxError
        
        for operand,operand_ref,operand_context in zip(operands,self.reference,self.context_template):
            if operand.type != operand_ref and operand.type_secondary != operand_ref:
                # operands mismatch
                raise SyntaxError
            # if the reference type is SYM, change it to the specific type
            if operand_ref == TokenTypes.SYM:
                types_context.append(operand.type_secondary)
            else:
                types_context.append(operand_context)
        return types_context


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
        try:
            if not self.context.next_token_buffer():
                # end of token stream
                raise MissingHeadError
            if len(self.context.token_buffer) != 1 or self.context.token_buffer[0].type != TokenTypes.HEAD:
                # header is not alone on the line or it is missing
                raise MissingHeadError
            else:
                return StateSetContext(self.context)
        except LexError:
            # lexical error in the first token means incorrectly written header
            raise MissingHeadError

class StateSetContext(State):
    _operand_references = {
        **dict.fromkeys(("MOVE", "STRLEN", "TYPE", "NOT", "INT2CHAR"),OperandsReference([TokenTypes.VAR, TokenTypes.SYM], None)),
        **dict.fromkeys(("CREATEFRAME", "PUSHFRAME", "POPFRAME", "RETURN"),OperandsReference([],None)),
        **dict.fromkeys(("PUSHS", "WRITE", "EXIT"),OperandsReference([TokenTypes.SYM],None)),
        **dict.fromkeys(("DEFVAR", "POPS"),OperandsReference([TokenTypes.VAR],None)),
        **dict.fromkeys(("ADD", "SUB", "MUL", "IDIV","LT", "GT", "EQ",
                      "AND", "OR", "STR2INT", "CONCAT", "GETCHAR", "SETCHAR", ),OperandsReference([TokenTypes.VAR, TokenTypes.SYM, TokenTypes.SYM],None)),
        **dict.fromkeys(("READ",),OperandsReference([TokenTypes.VAR, TokenTypes.TYPE],None)),
        # LABEL
        **dict.fromkeys(("LABEL", "CALL", "JUMP"),OperandsReference([TokenTypes.ALPHANUM], [TokenTypes.LABEL])),
        # LABEL SYM SYM
        **dict.fromkeys(("JUMPIFEQ", "JUMPIFNEQ"),OperandsReference([TokenTypes.ALPHANUM, TokenTypes.SYM, TokenTypes.SYM],[TokenTypes.LABEL, TokenTypes.SYM, TokenTypes.SYM])),
    }

    def handle(self):
        """
        Reads one line of tokens and changes their types based on the context (detected instruction opcode).
        Raises OpcodeError exception if the opcode cannot be determined.
        Raises SyntaxError exception if the arguments cannot be transformed based on the context
        """
        if not self.context.next_token_buffer():
            # end of token stream
            return StateFinish(self.context)
        if self.context.token_buffer[0].type == TokenTypes.HEAD:
            # unexpected header token
            raise SyntaxError

        opcode = self.context.token_buffer[0].string.upper()
        operands = self.context.token_buffer[1:]

        if not opcode in self._operand_references:
            raise OpcodeError

        operands_context = self._operand_references[opcode].compare(operands)

        # change the first token type to instruction type
        self.context.token_buffer[0].type = TokenTypes.INST
        # change the argument token types 
        for idx in range(0, len(operands_context)):
            # the tokens to be modified start on index 1, the token on index 0 is the opcode
            self.context.token_buffer[idx+1].type_context = operands_context[idx]

        return StateInstrBuild(self.context)

class StateInstrBuild(State):
    def _format_operand_string(self, operand):
        """
        Edit the token str for printing into the output XML tree
        Returns the formatted token string
        """
        if operand.type_context in [TokenTypes.INT, TokenTypes.BOOL, TokenTypes.STR, TokenTypes.NIL]:
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
            operand_el.set("type", operand.type_context.value)
            operand_el.text = self._format_operand_string(operand)

        self.context.instruction_cnter += 1
        return StateSetContext(self.context)

class StateFinish(State):
    endingState = True
    def handle(self):
        """
        Dumps the element tree in stdout
        """
        output_tree = ET.ElementTree(self.context.output_root)
        ET.indent(output_tree, space="\t", level=0)
        output_tree.write(sys.stdout.buffer, encoding="utf-8", xml_declaration=True)
