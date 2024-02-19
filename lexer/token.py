import re
from common.token_enums import TokenTypes
from common.exceptions import LexError

class Token:
    """
    Holds relevant information about the current token.
    Implements a Set method for correctly setting its atributes based on a word passed as an argument
    """
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

    def __init__(self, word) -> None:
        self.set_token(word)

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

    def set_token(self,word):
        self.type = self.__detect_token_type(word)
        self.string = word


class TokenIterator:
    """
    Iterator returning a list of tokens corresponding to one line in the input stream.
    On lexical error raises LexError exception.
    """
    def __init__(self, input_file) -> None:
        self.input_file = input_file

    def __iter__(self):
        while True:
            line = self.input_file.readline()

            if not line:
                break
            elif not line.strip():
                continue

            line = line.partition('#')[0]

            line_tokens = []

            for word in line.split():
                line_tokens.append(Token(word))

            yield line_tokens
