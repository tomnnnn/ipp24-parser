import sys
from dataclasses import dataclass, make_dataclass
from enum import Enum

class TokenTypes(Enum):
    INSTR = 1
    VAR = 2
    STR = 3
    
@dataclass
class Token:
    newline: bool
    type: TokenTypes
    string: str

class TokenIterator:
    current_token: Token

    def __init__(self, input_file) -> None:
        self.inputFile = input_file
        self.current_token = Token(True,TokenTypes.INSTR, "")

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
                
                yield self.current_token

    def __detect_token_type(self, string: str) -> TokenTypes:
        return TokenTypes.INSTR
    

input_file = sys.stdin
token_iter = TokenIterator(input_file)
counter = 0
for token in token_iter:
    print(str(counter) + " " + token.string)
    counter += 1

print(token_iter.current_token)
