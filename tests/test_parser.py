import unittest
from modl.parser import Parser
from modl.scanner import Scanner
from modl import expr


class PrimaryTests(unittest.TestCase):
    literals = {"5;": 5, '"five";': "five", "5.0;": 5.0}

    def test_literals(self):
        for string, literal in self.literals.items():
            with self.subTest(i=string):
                scanner = Scanner(string)
                parser = Parser(scanner.scan_tokens())
                statement = parser.statement()
                self.assertTrue(isinstance(statement, expr.Literal))
                self.assertEqual(statement.value, literal)

    def test_builtin(self):
        scanner = Scanner("{#print};")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Builtin))
        self.assertEqual(statement.name, "print")

    def test_identifier(self):
        scanner = Scanner("ident;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Identifier))
        self.assertEqual(statement.name, "ident")

    def test_symbols_cant_be_used_alone(self):
        scanner = Scanner("+;")
        parser = Parser(scanner.scan_tokens())
        with self.assertRaises(Exception):
            statement = parser.statement()

    def test_symbols_can_be_wrapped_in_parentheses(self):
        scanner = Scanner("(+);")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Identifier))
        self.assertEqual(statement.name, "+")

    def test_symbols_can_be_part_of_an_expression(self):
        scanner = Scanner("1 + 2;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Symchain))
        self.assertTrue(isinstance(statement.op, expr.Identifier))
        self.assertEqual(statement.op.name, "+")
        self.assertTrue(isinstance(statement.left, expr.Literal))
        self.assertEqual(statement.left.value, 1)
        self.assertTrue(isinstance(statement.right, expr.Literal))
        self.assertEqual(statement.right.value, 2)

    def test_parentheses_are_invisible(self):
        scanner = Scanner("(ident);")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Identifier))
        self.assertEqual(statement.name, "ident")

    def test_lambda(self):
        scanner = Scanner("{ x | x; };")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Function))
        self.assertEqual(len(statement.args), 1)
        self.assertEqual(len(statement.body), 1)

    def test_lambda_longer(self):
        scanner = Scanner("{ x y | x y; y x; x y;};")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Function))
        self.assertEqual(len(statement.args), 2)
        self.assertEqual(len(statement.body), 3)

    def test_lambda_cant_have_empty_parameter_list(self):
        scanner = Scanner("{ | 1; };")
        parser = Parser(scanner.scan_tokens())
        with self.assertRaises(Exception):
            statement = parser.statement()

    def test_lambda_cant_have_empty_body(self):
        scanner = Scanner("{ x | };")
        parser = Parser(scanner.scan_tokens())
        with self.assertRaises(Exception):
            statement = parser.statement()

    def test_cond(self):
        scanner = Scanner("cond | 1 -> 1; end;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Conditional))

    def test_cond_with_many_actions(self):
        scanner = Scanner("cond | x -> f x; 3; end;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Conditional))

    def test_cond_cant_be_empty(self):
        scanner = Scanner("cond end;")
        parser = Parser(scanner.scan_tokens())
        with self.assertRaises(Exception):
            statement = parser.statement()

    def test_cond_condition_cant_be_empty(self):
        scanner = Scanner("cond | -> x; end;")
        parser = Parser(scanner.scan_tokens())
        with self.assertRaises(Exception):
            statement = parser.statement()

    def test_cond_action_cant_be_empty(self):
        scanner = Scanner("cond | x -> end;")
        parser = Parser(scanner.scan_tokens())
        with self.assertRaises(Exception):
            statement = parser.statement()

    def test_bangs_are_special(self):
        scanner = Scanner("!;")
        parser = Parser(scanner.scan_tokens())
        with self.assertRaises(Exception):
            statement = parser.statement()
            print(statement)

    def test_things_can_have_types(self):
        scanner = Scanner("ident : Integer;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertEqual(len(statement.types), 1)
        self.assertEqual(statement.types[0], "Integer")

    def test_lambdas_can_have_types(self):
        scanner = Scanner("{ x | x; } : Integer -> Integer;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertEqual(len(statement.types), 2)
        self.assertEqual(statement.types[0], "Integer")
        self.assertEqual(statement.types[1], "Integer")

    def things_can_have_types_in_the_middle_of_other_things(self):
        scanner = Scanner("ident : Integer + 5;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Expression))
        self.assertEqual(statement[0].name, "ident")
        self.assertEqual(len(statement[0].types), 1)
        self.assertEqual(statement[0].types[0], "Integer")


class FuncallTests(unittest.TestCase):
    def test_simple_call(self):
        scanner = Scanner("call par1 2;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()

        self.assertTrue(isinstance(statement, expr.Expression))
        self.assertEqual(len(statement.call), 3)

        self.assertTrue(isinstance(statement.call[0], expr.Identifier))
        self.assertEqual(statement.call[0].name, "call")

        self.assertTrue(isinstance(statement.call[1], expr.Identifier))
        self.assertEqual(statement.call[1].name, "par1")

        self.assertTrue(isinstance(statement.call[2], expr.Literal))
        self.assertEqual(statement.call[2].value, 2)

    def test_bang_words_are_magic(self):
        scanner = Scanner("print!;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()

        self.assertTrue(isinstance(statement, expr.Expression))
        self.assertEqual(len(statement.call), 2)

        self.assertTrue(isinstance(statement.call[0], expr.Identifier))
        self.assertEqual(statement.call[0].name, "print!")

        self.assertTrue(isinstance(statement.call[1], expr.Identifier))
        self.assertEqual(statement.call[1].name, "!")

    def test_complete_your_function(self):
        scanner = Scanner("{ x | x; ")
        parser = Parser(scanner.scan_tokens())
        with self.assertRaises(Exception):
            statement = parser.statement()

    def test_simplest_program(self):
        scanner = Scanner("1;")
        parser = Parser(scanner.scan_tokens())
        program = parser.program()
        self.assertEqual(len(program), 1)

        statement = program[0]
        self.assertTrue(isinstance(statement, expr.Literal))
        self.assertEqual(statement.value, 1)


class StatementTests(unittest.TestCase):
    def test_use(self):
        scanner = Scanner('use "potato";')
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Use))
        self.assertEqual(statement.filename, "potato")

    def test_single(self):
        scanner = Scanner("let a <- 1;")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Let))
        self.assertEqual(len(statement.assignments), 1)
        name, value = statement.assignments[0]
        self.assertTrue(isinstance(name, expr.Identifier))
        self.assertTrue(isinstance(value, expr.Literal))

    def test_multiple(self):
        scanner = Scanner("let a <- 1, + <- { x y | x y; };")
        parser = Parser(scanner.scan_tokens())
        statement = parser.statement()
        self.assertTrue(isinstance(statement, expr.Let))
        self.assertEqual(len(statement.assignments), 2)
        name, value = statement.assignments[0]
        self.assertTrue(isinstance(name, expr.Identifier))
        self.assertTrue(isinstance(value, expr.Literal))
        name, value = statement.assignments[1]
        self.assertTrue(isinstance(name, expr.Identifier))
        self.assertTrue(isinstance(value, expr.Function))

    def test_cant_assign_to_a_function(self):
        scanner = Scanner("let { x | x; }; <- 1;")
        parser = Parser(scanner.scan_tokens())
        with self.assertRaises(Exception):
            statement = parser.statement()


class GreenspunTest(unittest.TestCase):
    program = """
    use "std.dl";
    let x <- 1 : Integer, f <- { a | {#add} x + a; };
    f (+) x;
    cond
    | a -> f x 1;
    | b -> print! "B";
           (+);
    end;
    """
    output = """USE 'std.dl'
(DEFINE x 1
        f (LAMBDA (a) (+ (#add x) a)))
(f + x)
(COND (a (f x 1)) (b(progn
(print! ! 'B')
+)) )"""

    def test_hey_this_looks_like_lisp_lol(self):
        scanner = Scanner(self.program)
        parser = Parser(scanner.scan_tokens())
        program = parser.program()
        self.assertEqual("\n".join(repr(st) for st in program), self.output)
