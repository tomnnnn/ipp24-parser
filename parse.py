from parser.parser import Parser
from lexer.token import *
import sys

argc = len(sys.argv)
if argc == 2 and sys.argv[1] == '--help':
    print('This filter type script loads IPPcode24 source code from stdin, checks its lexical and syntactic correctness and prints its XML representation in stdout')
    sys.exit(0)
elif argc == 1:
    tokens = TokenIterator(sys.stdin)
    parse = Parser(tokens)
    parse.parse()
    sys.exit(0)
else:
    # invalid command line argument combination
    print('Invalid argument(s). Use: parse.py [--help]', file=sys.stderr)
    sys.exit(10)

