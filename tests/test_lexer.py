import unittest
from .test_exceptions import TestException
from io import StringIO

from lexer.token import TokenIterator
from common.token_enums import TokenTypes
from common.exceptions import LexError


class LexerTests(unittest.TestCase):
    def _tokens_from_string(self,inputStr):
        f = StringIO(inputStr)
        return TokenIterator(f)
    
    def _incorrect_input_test(self,inputStr):
        """Asserts lexical incorrectness of a given string"""
        tokens = self._tokens_from_string(inputStr)

        with self.assertRaises(LexError,msg="Lexer failed to detect lexical error: "+inputStr):
            for token in tokens:
                pass
    def _correct_input_test(self,inputStr,tokenType):
        """
        Compares token types given by the TokenIterator against token types passed by the argument tokenType.
        Expects a lexically correct string.
        """
        tokens = iter(self._tokens_from_string(inputStr))

        for type in tokenType:
            try:
                token = next(tokens)
                self.assertTrue(type == token.type)
            except LexError:
                self.fail("TokenIterator raised LexError unexpectedly: "+inputStr)

        try:
            next(tokens)
        except StopIteration:
            pass
        else:
            raise TestException("Lexer returned more tokens than expected")

    # Tests ----------------------------------

    def test_alphanum_incorrect(self):
        self._incorrect_input_test("$MOV")
        self._incorrect_input_test("4MOV")
        self._incorrect_input_test("alphanum@alphanum")

    def test_alphanum_correct(self):
        self._correct_input_test("MOV$", [TokenTypes.ALPHANUM])
        self._correct_input_test("MOV42",[TokenTypes.ALPHANUM])
        self._correct_input_test("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",[TokenTypes.ALPHANUM])
        self._correct_input_test("      ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789      ",[TokenTypes.ALPHANUM])

        self._correct_input_test("alpha num tokens\nalphanum", [TokenTypes.ALPHANUM, TokenTypes.ALPHANUM, TokenTypes.ALPHANUM, TokenTypes.ALPHANUM])

    def test_var_incorrect(self):
        self._incorrect_input_test("lf@var@var")
        self._incorrect_input_test("gf@@var")
        self._incorrect_input_test("gf@")

    def test_var_correct(self):
        self._correct_input_test("LF@var",[TokenTypes.VAR])
        self._correct_input_test("lf@var",[TokenTypes.VAR])
        self._correct_input_test("GF@var",[TokenTypes.VAR])
        self._correct_input_test("gf@var",[TokenTypes.VAR])

        self._correct_input_test("gf@var42",[TokenTypes.VAR])
        self._correct_input_test("gf@var#",[TokenTypes.VAR])
        self._correct_input_test("gf@var-var",[TokenTypes.VAR])
        self._correct_input_test("gf@snake_case",[TokenTypes.VAR])
    
    def test_string_incorrect(self):
        self._incorrect_input_test("string@\\")
        self._incorrect_input_test("string@\\2")
        self._incorrect_input_test("string@retezec\\")
        self._incorrect_input_test("STRING@retezec")

    def test_string_correct(self):
        self._correct_input_test("string@string", [TokenTypes.STR])
        self._correct_input_test("string@012", [TokenTypes.STR])
        self._correct_input_test("string@\\012", [TokenTypes.STR])
        self._correct_input_test("string@ahoj\\100ahoj", [TokenTypes.STR])
        self._correct_input_test("string@!@$%^&*(ahoj123", [TokenTypes.STR])

    def test_bool_incorrect(self):
        self._incorrect_input_test("BOOL@false")
        self._incorrect_input_test("bool@False")
        self._incorrect_input_test("bool@True")
        self._incorrect_input_test("bool@")

    def test_bool_correct(self):
        self._correct_input_test("bool@false", [TokenTypes.BOOL])
        self._correct_input_test("bool@true", [TokenTypes.BOOL])

    def test_int_incorrect(self):
        self._incorrect_input_test("int@")
        self._incorrect_input_test("INT@2")
        self._incorrect_input_test("int@0x-20")
        self._incorrect_input_test("int@a")
        self._incorrect_input_test("int@2__2")
        self._incorrect_input_test("int@_2")
        self._incorrect_input_test("int@2_")
        self._incorrect_input_test("int@_")

    def test_int_correct(self):
        self._correct_input_test("int@42", [TokenTypes.INT])
        self._correct_input_test("int@0x42abc", [TokenTypes.INT])
        self._correct_input_test("int@0o7", [TokenTypes.INT])
        self._correct_input_test("int@-42", [TokenTypes.INT])
        self._correct_input_test("int@-0x42", [TokenTypes.INT])
        self._correct_input_test("int@-0o42", [TokenTypes.INT])
        self._correct_input_test("int@100_000", [TokenTypes.INT])
        self._correct_input_test("int@0052", [TokenTypes.INT])

    def test_comments(self):
        self._correct_input_test("#",[])
        self._correct_input_test("# int@42", [])
        self._correct_input_test("int@42 # int@20", [TokenTypes.INT])
        self._correct_input_test("#\nint@42", [TokenTypes.INT])

    def test_multiple(self):
        self._correct_input_test("""
                              MOVE lf@var int@42 # comment


                              CONCAT GF@counter GF@counter string@a
                                        LABEL while
                              # comment
                              """,[TokenTypes.ALPHANUM, TokenTypes.VAR, TokenTypes.INT,
                                   TokenTypes.ALPHANUM, TokenTypes.VAR, TokenTypes.VAR,
                                   TokenTypes.STR,TokenTypes.ALPHANUM,TokenTypes.ALPHANUM])

if __name__ == "__main__":
    unittest.main()
