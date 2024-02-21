from enum import Enum, auto

class TokenTypes(Enum):
    """Enumeration for differentiating token types"""
    VAR = 'var'
    LABEL = 'label'
    TYPE = 'type'
    STR = 'string'
    INT = 'int'
    NIL = 'nil'
    BOOL = 'bool'
    HEAD = auto()
    ALPHANUM = auto()
    ERR = auto()
    INST = auto()
    SYM = auto()
    NONE = auto()

