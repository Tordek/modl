import os
import sys
import unittest
from modl.scanner import Scanner
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

    valid_floats = {"0.0": 0.0, "0.1": 0.1, "1.0": 1.0, ".5": 0.5, "-.5": -0.5}

    valid_strings = {
        r'""': "",
        r'"a"': "a",
        r'"this is a long string"': "this is a long string",
        '"this string\nis multiline"': "this string\nis multiline",
        r'"this string\nis also multiline"': "this string\nis also multiline",
        r'"A whole bunch of escape sequences \r\n\t\\\"\x0123"': 'A whole bunch of escape sequences \r\n\t\\"\u0123',
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

    valid_symbols = [
        "-->",
        "<--",
        "?",
        "!!",
        "::",
        "||",
        "&&",
        "->>",
        "=*>>",
        "-",
        "-.",
        ".",
        "..",
        "-..",
        "--",
        "/",
        "//",
        "' ",
    ]
    valid_identifiers = ["foo", "bar_baz", "quux'", "read!", "add4", "plus5!"]

    # Sequences containing unique characters that may not be part of a symbol
    invalid_symbols = ["-{", "/a", "-)", "+,+"]

    def test_valid_integers(self):
        for string, literal in self.valid_integers.items():
            with self.subTest(i=string):
                scanner = Scanner(string)
                tokens = scanner.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, TokenType.B10_INTEGER)
                self.assertEqual(token.literal, literal)

    def test_valid_floats(self):
        for string, literal in self.valid_floats.items():
            with self.subTest(i=string):
                scanner = Scanner(string)
                tokens = scanner.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, TokenType.B10_FLOAT)
                self.assertEqual(token.literal, literal)

    def test_valid_strings(self):
        for string, literal in self.valid_strings.items():
            with self.subTest(i=string):
                scanner = Scanner(string)
                tokens = scanner.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, TokenType.STRING)
                self.assertEqual(token.literal, literal)

    def test_reserved_sequences(self):
        for string, token_type in self.reserved.items():
            with self.subTest(i=string):
                scanner = Scanner(string)
                tokens = scanner.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, token_type)

    def test_valid_symbol(self):
        for string in self.valid_symbols:
            with self.subTest(i=string):
                scanner = Scanner(string)
                tokens = scanner.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, TokenType.SYMBOLIC)

    def test_invalid_symbol(self):
        for string in self.invalid_symbols:
            with self.subTest(i=string):
                scanner = Scanner(string)
                tokens = scanner.scan_tokens()
                # Whatever this matched is OK as long as it's not a single symbol
                self.assertNotEqual(len(tokens), 2)

    def test_valid_identifier(self):
        for string in self.valid_identifiers:
            with self.subTest(i=string):
                scanner = Scanner(string)
                tokens = scanner.scan_tokens()
                self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
                token = tokens[0]
                self.assertIs(token.token_type, TokenType.IDENTIFIER)

    def test_single_line(self):
        scanner = Scanner("foobar")
        scanner.scan_tokens()  # Discard
        self.assertEqual(scanner.line, 1)

    def test_two_lines(self):
        scanner = Scanner("foo\nbar")
        scanner.scan_tokens()  # Discard
        self.assertEqual(scanner.line, 2)

    def test_multiple_lines(self):
        scanner = Scanner(
            r"""this is a "series of
        tokens"
        /* including multiline comments
        spread
        among several */
        lines, also "includes an \n escaped linebreak character" that should be ignored"""
        )
        scanner.scan_tokens()  # Discard
        self.assertEqual(scanner.line, 6)

    def test_builtin(self):
        scanner = Scanner("{#builtin_name}")
        tokens = scanner.scan_tokens()
        self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
        token = tokens[0]
        self.assertIs(token.token_type, TokenType.BUILTIN)
        self.assertEqual(token.literal, "builtin_name")

    def test_typename(self):
        scanner = Scanner("Type")
        tokens = scanner.scan_tokens()
        self.assertEqual(len(tokens), 2)  # Parsed symbol, plus EOF
        token = tokens[0]
        self.assertIs(token.token_type, TokenType.TYPENAME)
        self.assertEqual(token.lexeme, "Type")


class InvalidTokensTest(unittest.TestCase):
    def test_unclosed_comment(self):
        scanner = Scanner("/* unclosed comment")
        with self.assertRaises(Exception):
            scanner.scan_tokens()

    def test_unopened_comment(self):
        scanner = Scanner("forgot to remove uncomment */")
        with self.assertRaises(Exception):
            scanner.scan_tokens()

    def test_unclosed_string(self):
        scanner = Scanner('"a string with no close')
        with self.assertRaises(Exception):
            scanner.scan_tokens()

    def test_incomplete_string_escape(self):
        scanner = Scanner('"unclosed escape\\')
        with self.assertRaises(Exception):
            scanner.scan_tokens()

    def test_invalid_escape_sequence(self):
        scanner = Scanner(r'"invalid escape \q code"')
        with self.assertRaises(Exception):
            scanner.scan_tokens()

    def test_invalid_unicode_escape_sequence(self):
        scanner = Scanner(r'"invalid escape \x15')
        with self.assertRaises(Exception):
            scanner.scan_tokens()

    def test_unclosed_builtin(self):
        scanner = Scanner(r"{#broken_builtin")
        with self.assertRaises(Exception):
            scanner.scan_tokens()

    def test_bang_after_keyword(self):
        scanner = Scanner(r"let!")
        with self.assertRaises(Exception):
            scanner.scan_tokens()


class ExprTest(unittest.TestCase):
    def test_literal_expression(self):
        scanner = Scanner("{#builtin_name}")
        tokens = scanner.scan_tokens()
        self.assertEqual(repr(tokens[0]), "TokenType.BUILTIN '{#builtin_name}'")

    def test_other_expression(self):
        scanner = Scanner("+")
        tokens = scanner.scan_tokens()
        self.assertEqual(repr(tokens[0]), "TokenType.SYMBOLIC '+' None")
