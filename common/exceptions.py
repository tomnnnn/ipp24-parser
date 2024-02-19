class LexError(Exception):
    """Signals a lexical error in the input"""

class SyntaxError(Exception):
    pass

class OpcodeError(Exception):
    pass

class MissingHeadError(Exception):
    pass
