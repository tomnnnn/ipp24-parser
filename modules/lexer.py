import sys

class Token():
    def __init__(self, instruction, operands) -> None:
        self.instruction = instruction
        self.operands = operands

class Lexer():
    """
    Lexer converts plain text code from a given source file to a tokenized instruction.
    It ignores empty lines and removes comments in the process.
    """
    def __init__(self, inputFile) -> None:
        self.inputFile = inputFile

    def __read_instruction(self):
        '''Returns next non-empty line stripped from comments'''
        line = self.inputFile.readline()
        
        # skip empty lines or while line comment
        while(line.strip() == "" or line[0] == '#'):
            line = self.inputFile.readline()
        
        return line

    def __tokenize_instruction(self, instruction):
        '''Converts string instruction into a token object'''
        # TODO
        return instruction

    def next_instruction(self):
        '''Returns next instruction in a tokenized form'''
        instruction = self.__read_instruction()
        token = self.__tokenize_instruction(instruction)
        if(token != None):
            return token
        else:
            sys.exit(0);
