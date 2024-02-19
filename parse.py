from parser.parser import Parser
from lexer.token import *
import sys

tokens = TokenIterator(sys.stdin)
parse = Parser(tokens)
parse.parse()

