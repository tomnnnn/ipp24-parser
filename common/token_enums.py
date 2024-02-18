from enum import Enum, auto

class TokenTypes(Enum):
    """Enumeration for differentiating token types"""
    HEAD = auto()
    ALPHANUM = auto()
    VAR = auto()
    STR = auto()
    INT = auto()
    BOOL = auto()
    ERR = auto()
    
