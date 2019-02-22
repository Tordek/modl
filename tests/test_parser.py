import unittest
from modl.parser import Parser
from modl.scanner import Scanner

class PrimitivesTests(unittest.TestCase):
    def test_literal(self):
        scanner = Scanner("5")
        parser = Parser(scanner.scan_tokens())
