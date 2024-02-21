import re
from common.token_enums import TokenTypes
from common.exceptions import LexError

class Token:
    """
    Holds relevant information about the current token.
    Implements a Set method for correctly setting its atributes based on a word passed as an argument
    """
    type: TokenTypes
    type_secondary: TokenTypes
    type_context : TokenTypes
    string: str
            
    # regex for token types definitions
    _type_regex = {
        TokenTypes.HEAD : r'^.IPPcode24$',
        TokenTypes.ALPHANUM : r'^[a-zA-Z][\w$%*!?-]*$',
        TokenTypes.SYM : r'^[^@]+@.*'
    }

    _secondary_sym_regex = {
        TokenTypes.VAR : r'^(LF|GF|TF)@[a-zA-z][\w$%*!?-]*$',
        TokenTypes.STR : r'^string@([^\s#\\]*(\\\d{3})*)*$',
        TokenTypes.INT : r'^int@-?(((\d+_?)+)|(0o([0-7]+_?)+)|(0x([\da-fA-F]+_?)+))$',
        TokenTypes.NIL : r'^nil@nil$',
        TokenTypes.BOOL : r'^bool@(false|true)$'
    }

    _secondary_alphanum_regex = {
        TokenTypes.TYPE : r'^(int|bool|string)$',
    }

    _const_type_regex = {
    }

    def __init__(self, word) -> None:
        self.set_token(word)

    def _detect_token_type(self, string: str) -> TokenTypes:
        """
        Determines the type of token from the currently processed word. 
        If a type cannot be determined, raises LexError exception
        """
        for type in self._type_regex:
            if re.match(self._type_regex[type],string):
                return type
        raise LexError

    def _detect_type_sec_type(self, string: str, regex_patterns : dict) -> TokenTypes:
        """
        some token types can be further classified into secondary types
        """
        for type in regex_patterns:
            if re.match(regex_patterns[type],string):
                return type
        return TokenTypes.NONE


    def set_token(self,word):
        self.type = self._detect_token_type(word)
        if(self.type == TokenTypes.ALPHANUM):
            self.type_secondary = self._detect_type_sec_type(word, self._secondary_alphanum_regex)
        if(self.type == TokenTypes.SYM):
            self.type_secondary = self._detect_type_sec_type(word, self._secondary_sym_regex)

            # sym must have a secondary type, otherwise it is a lexical error
            if self.type_secondary == TokenTypes.NONE:
                raise LexError
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

            line = line.partition('#')[0]
            if not line.strip():
                continue


            line_tokens = []

            for word in line.split():
                line_tokens.append(Token(word))

            yield line_tokens
