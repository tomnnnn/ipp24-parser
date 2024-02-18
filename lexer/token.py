import re
from dataclasses import dataclass

from common.token_enums import TokenTypes
from common.exceptions import LexError

@dataclass
class Token:
    """
    Holds relevant information about the current token.
    Implements a Set method for correctly setting its atributes based on a word passed as an argument
    """
    newline: bool
    type: TokenTypes
    string: str
            
    # regex for token types definitions
    _typeRegex = {
        TokenTypes.HEAD : r'^.IPPcode24$',
        TokenTypes.ALPHANUM : r'^[a-zA-Z][\w$%*!?-]*$',
        TokenTypes.VAR : r'^(?i:(LF|GF))@[a-zA-z][\w$%*!?-]*$',
        TokenTypes.STR : r'^string@([^\s#\\]*(\\\d{3})?)*$',
        TokenTypes.INT : r'^int@.+$',
        TokenTypes.BOOL : r'^bool@(false|true)$'
    }

    def __detect_token_type(self, string: str) -> TokenTypes:
        """
        Determines the type of token from the currently processed word. 
        If a type cannot be determined, raises LexError.
        """
        for type in self._typeRegex:
            if re.match(self._typeRegex[type],string):
                if(type == TokenTypes.INT):
                    # additional integer format check
                    try:
                        int(string.split('@')[1],0)
                    except ValueError:
                        continue
                return type
        raise LexError

    def Set(self,word,newline):
        self.newline = newline
        self.type = self.__detect_token_type(word)
        self.string = word


class TokenIterator:
    """
    Iterator returning next token in the input stream. The input stream file is defined in the constructor.
    On lexical error raises LexError exception
    """
    current_token: Token

    def __init__(self, input_file) -> None:
        self.inputFile = input_file
        self.current_token = Token(True,TokenTypes.ALPHANUM, '')

    def __iter__(self):
        while True:
            line = self.inputFile.readline()
            if not line:
                break
            line = line.partition('#')[0]

            newline = True
            for word in line.split():
                self.current_token.Set(word,newline)
                newline = False

                yield self.current_token
