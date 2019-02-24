import unittest

from collections import ChainMap
from modl import interpreter
from modl.scanner import Scanner
from modl.parser import Parser

class InterpretAllTheThings(unittest.TestCase):
    def test_use(self):
        env = ChainMap()
        env["!"] = "!"
        env["otherwise"] = True
        env["true"] = True
        env["false"] = False

        scanner = Scanner('use "std.dl";')
        parser = Parser(scanner.scan_tokens())
        result, env = interpreter.interpret(parser.statement(), env)
        self.assertEqual(result, None)
        self.assertIn("print!", env)

    def test_fibo(self):
        env = ChainMap()
        env["!"] = "!"
        env["otherwise"] = True
        env["true"] = True
        env["false"] = False

        scanner = Scanner('use "test.dl"; fibo 5;')
        parser = Parser(scanner.scan_tokens())
        for statement in parser.program():
            result, env = interpreter.interpret(statement, env)
        self.assertEqual(result, 8)

    def test_deep(self):
        env = ChainMap()
        env["!"] = "!"
        env["otherwise"] = True
        env["true"] = True
        env["false"] = False

        scanner = Scanner('use "test.dl"; flatfibo 500;')
        parser = Parser(scanner.scan_tokens())
        for statement in parser.program():
            result, env = interpreter.interpret(statement, env)

        self.assertIsNotNone(result)

    def test_multideep(self):
        env = ChainMap()
        env["!"] = "!"
        env["otherwise"] = True
        env["true"] = True
        env["false"] = False

        scanner = Scanner('use "test.dl"; tracefibo 1 1 5;')
        parser = Parser(scanner.scan_tokens())
        for statement in parser.program():
            result, env = interpreter.interpret(statement, env)
        self.assertEqual(result, 8)
