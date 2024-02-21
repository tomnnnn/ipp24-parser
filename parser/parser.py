import sys
from collections.abc import Iterator
from common.exceptions import *
from common.token_enums import *
from .states import *
from xml.etree import ElementTree as ET

class Parser:
    instruction_cnter : int
    token_buffer : list
    output_root : ET.Element
    _tokens : Iterator
    _state : State

    def __init__(self, tokens) -> None:
        self.instruction_cnter = 1
        self.token_buffer = []
        self._state = StateHeader(self)
        self._tokens = iter(tokens)
        self.output_root = ET.Element('program')
        self.output_root.set('language', 'IPPcode24')

    def parse(self):
        try:
            while not self._state.endingState:
                self._handle_state()
            # handle ending state and exit
            self._handle_state()
        except MissingHeadError:
            print("Error: Missing head", file=sys.stderr)
            sys.exit(21)
        except OpcodeError:
            print("Error: Unknown opcode or invalid operands combination", file=sys.stderr)
            sys.exit(22)
        except (LexError, SyntaxError):
            print("Error: Other lexical or syntax error", file=sys.stderr)
            sys.exit(23)

    def next_token_buffer(self):
        try:
            self.token_buffer = next(self._tokens)
            return True
        except StopIteration:
            return False

    def _handle_state(self):
        self._transition_state(self._state.handle())
    
    def _transition_state(self, state):
        self._state = state
