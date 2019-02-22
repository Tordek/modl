import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import unittest
from modl import scanner
from modl.tokens import TokenType


class TestScannerTokens(unittest.TestCase):
    valid_integers = {
        "0": 0,
        "1": 1,
        "1234567890": 1234567890,
        "12345678901234567890": 12345678901234567890,
        "-1": -1,
        "-0": 0,  # Pointless, but valid
        "000123": 123,
        "-000123": -123,
    }

    valid_floats = {
        "0.0": 0.0,
        "0.1": 0.1,
        "1.0": 1.0,
        ".5": 0.5,
        "-.5": -0.5,
    }
    
    valid_strings = {
        r'""': "",
        r'"a"': "a",
        r'"this is a long string"': "this is a long string",
        '"this string\nis multiline"': "this string\nis multiline",
        r'"this string\nis also multiline"': "this string\nis also multiline",
    }

    reserved = {
        "use": TokenType.USE,
        "let": TokenType.LET,
        "end": TokenType.END,
        "cond": TokenType.COND,
        "<-": TokenType.LEFT_ARROW,
        "->": TokenType.RIGHT_ARROW,
        "|": TokenType.PIPE,
        ":": TokenType.COLON,
        "!": TokenType.BANG,
        ";": TokenType.SEMICOLON,
        "{": TokenType.OPEN_BRACKETS,
        "}": TokenType.CLOSE_BRACKETS,
        "(": TokenType.OPEN_PARENTHESES,
        ")": TokenType.CLOSE_PARENTHESES,
        ",": TokenType.COMMA,
    }

    valid_symbols = ["-->", "<--", "?", "!!", "::", "||", "&&", "->>", "=*>>", "-", "-.", ".", "..", "-..", "--"]
    
    def test_valid_integers(self):
        for string, literal in self.valid_integers.items():
            with self.subTest(i=string):
                scanner_ = scanner.Scanner(string)
                tokens = scanner_.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, TokenType.B10_INTEGER)
                self.assertEqual(token.literal, literal)

    def test_valid_floats(self):
        for string, literal in self.valid_floats.items():
            with self.subTest(i=string):
                scanner_ = scanner.Scanner(string)
                tokens = scanner_.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, TokenType.B10_FLOAT)
                self.assertEqual(token.literal, literal)
                
    def test_valid_strings(self):
        for string, literal in self.valid_strings.items():
            with self.subTest(i=string):
                scanner_ = scanner.Scanner(string)
                tokens = scanner_.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, TokenType.STRING)
                self.assertEqual(token.literal, literal)

    def test_reserved_sequences(self):
        for string, token_type in self.reserved.items():
            with self.subTest(i=string):
                scanner_ = scanner.Scanner(string)
                tokens = scanner_.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, token_type)

    def test_valid_symbol(self):
        for string in self.valid_symbols:
            with self.subTest(i=string):
                scanner_ = scanner.Scanner(string)
                tokens = scanner_.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, TokenType.SYMBOLIC)

    def test_single_line(self):
        scanner_ = scanner.Scanner("foobar");
        scanner_.scan_tokens()  # Discard
        self.assertEqual(scanner_.line, 1)
                
    def test_two_lines(self):
        scanner_ = scanner.Scanner("foo\nbar");
        scanner_.scan_tokens()  # Discard
        self.assertEqual(scanner_.line, 2)

    def test_multiple_lines(self):
        scanner_ = scanner.Scanner(r"""this is a "series of
        tokens"
        spread
        among several
        lines, also "includes an \n escaped linebreak character" that should be ignored""");
        scanner_.scan_tokens()  # Discard
        self.assertEqual(scanner_.line, 5)
        
if __name__ == "__main__":
    
    unittest.main()
