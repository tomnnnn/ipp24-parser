import sys
import re
from dataclasses import dataclass
from enum import Enum, auto


class TokenTypes(Enum):
    HEAD = auto()
    ALPHANUM = auto()
    VAR = auto()
    STR = auto()
    INT = auto()
    BOOL = auto()
    NONE = auto()
    
@dataclass
class Token:
    newline: bool
    type: TokenTypes
    string: str

class TokenIterator:
    current_token: Token

    def __init__(self, input_file) -> None:
        self.inputFile = input_file
        self.current_token = Token(True,TokenTypes.ALPHANUM, '')
        
        # regex for token types definitions
        self.typeReg = {
            TokenTypes.HEAD : r'.IPPcode24',
            TokenTypes.ALPHANUM : r'^[a-zA-Z][\w$%*!?-]*$',
            TokenTypes.VAR : r'^(?i:(LF|GF))@[a-zA-z][\w$%*!?-]*$',
            TokenTypes.STR : r'^string@[^\s#]*$',
            TokenTypes.INT : r'^int@-?(0x|0o)?\d+(_\d+)*$',
            TokenTypes.BOOL : r'bool@(false|true)'
       }

    def __iter__(self):
        while True:
            line = self.inputFile.readline()
            if not line:
                break
            line = line.partition('#')[0]

            newline = True
            for word in line.split():
                self.current_token.newline = newline
                self.current_token.type = self.__detect_token_type(word)
                self.current_token.string = word
                
                newline = False
                yield self.current_token

    def __detect_token_type(self, string: str) -> TokenTypes:
        for type in self.typeReg:
            if re.match(self.typeReg[type],string):
                if(type == TokenTypes.INT):
                    # additional integer format check
                    try:
                        int(string.split('@')[1],0)
                    except ValueError:
                        continue
                return type
        return TokenTypes.NONE
    

input_file = sys.stdin
token_iter = TokenIterator(input_file)
counter = 0
for token in token_iter:
    print(str(counter), end=' ')
    print(token)
    counter += 1
