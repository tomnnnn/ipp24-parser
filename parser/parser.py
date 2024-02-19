import sys
from abc import ABC, abstractmethod
from common import exceptions
from lexer.token import TokenIterator, Token
from common.token_enums import TokenTypes
from common.exceptions import *


class State(ABC):
    endingState = False

    def __init__(self, context) -> None:
        self.context = context

    @abstractmethod
    def exec(self) -> object:
        pass

class StateHeader(State):
    def exec(self):
        tokens_line = next(self.context.tokens)

        if len(tokens_line) != 1 or tokens_line[0].type != TokenTypes.HEAD:
            raise MissingHeadError
        else:
            return StateInstruction(self.context)

class StateInstruction(State):
    instructions = {
        "MOVE": [
            [TokenTypes.VAR, TokenTypes.INT],
            [TokenTypes.VAR, TokenTypes.STR],
            [TokenTypes.VAR, TokenTypes.BOOL]
        ],
    }
    def exec(self):
        try:
            tokens_line = next(self.context.tokens)
        except StopIteration:
            return StateFinish(self.context)

        opcode = tokens_line[0].string.upper()
        operands = [token.type for token in tokens_line[1:]]
        if not opcode in self.instructions:
            raise OpcodeError
        else:
            for operand_rules in self.instructions[opcode]:
                if operands == operand_rules:
                    # success
                    print(opcode + " is a correct instruction with correct operands")
                    return StateInstruction(self.context)
            raise SyntaxError

class StateFinish(State):
    endingState = True
    def exec(self):
        print("Finished")

class Parser:
    tokens : TokenIterator
    _state : State
    instruction : str

    def __init__(self, tokens) -> None:
        self._state = StateHeader(self)
        self.tokens = iter(tokens)

    def parse(self):
        try:
            while not self._state.endingState:
                self._exec_state()

            self._exec_state()
        except MissingHeadError:
            print("Error: Missing head", file=sys.stderr)
            sys.exit(21)
        except OpcodeError:
            print("Error: Unknown opcode", file=sys.stderr)
            sys.exit(22)
        except (LexError, SyntaxError):
            print("Error: Other lexical or syntax error", file=sys.stderr)
            sys.exit(23)


    def _exec_state(self):
        self._transition_state(self._state.exec())

    
    def _transition_state(self, state):
        self._state = state

inputStr = sys.stdin
tokens = TokenIterator(inputStr)
parser = Parser(tokens)
