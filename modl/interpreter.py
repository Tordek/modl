import collections
from . import expr as expr
from .parser import Parser
from .scanner import Scanner

BUILTIN = {
    "print": lambda x: print(x),
    "add": lambda x, y: x + y,
    "sub": lambda x, y: x - y,
    "read": lambda _: input(),
    "eq": lambda x, y: x == y,
    "gt": lambda x, y: x > y,
    "if": lambda c, t, f: t if c else f,
}


class Function:
    def __init__(self, function, environment):
        self.function = function
        self.environment = environment


class Interpreter:
    def interpret(self, statement, environment):
        if isinstance(statement, expr.Literal):
            return (statement.value, environment)
        elif isinstance(statement, expr.Identifier):
            return (environment[statement.name], environment)
        elif isinstance(statement, expr.Grouping):
            return self.interpret(statement.expression, environment)
        elif isinstance(statement, expr.Function):
            return (Function(statement, environment), environment)
        elif isinstance(statement, expr.Builtin):
            return (BUILTIN[statement.name], environment)
        elif isinstance(statement, expr.Expression):
            results = []
            for s in statement.call:
                result, _ = self.interpret(s, environment)
                results.append(result)
            if len(results) == 1:
                return (results[0], environment)
            else:
                return (self.do_call(*results), environment)
        elif isinstance(statement, expr.Symchain):
            (left, _) = self.interpret(statement.left, environment)
            (op, _) = self.interpret(statement.op, environment)
            (right, _) = self.interpret(statement.right, environment)
            return (self.do_call(op, left, right), environment)
        elif isinstance(statement, expr.Use):
            with open(statement.filename) as file:
                contents = file.read()
                scanner = Scanner(contents)
                parser = Parser(scanner.scan_tokens())
                for statement in parser.program():
                    result, environment = self.interpret(statement, environment)
                return (result, environment)
        elif isinstance(statement, expr.Let):
            environment = environment.new_child()
            for (name, value) in statement.assignments:
                (evaluated_value, _) = self.interpret(value, environment)
                environment[name.name] = evaluated_value
            return (None, environment)
        elif isinstance(statement, expr.Conditional):
            # Discard the environment from the evaluation
            # to disallow `let`s done inside a case
            for condition, body in statement.cases:
                value, _ = self.interpret(condition, environment)
                if value is True:
                    env = environment
                    for st in body:
                        result, env = self.interpret(st, env)
                    return result, environment
                elif value is False:
                    continue
                else:
                    raise Exception("Type mismatch, condition must be boolean")
        else:
            raise Exception("Trying to run unknown thing", statement)

    def do_call(self, f, *params):
        # Currying, but optimized if there are multiple parameters
        if isinstance(f, Function):
            f_env = f.environment.new_child()
            args = f.function.args
            for name, value in zip(args, params):
                f_env[name.name] = value
            if len(args) > len(params):
                return Function(expr.Function(args[len(params) :], f.function.body), f_env)
            else:
                v = None
                for statement in f.function.body:
                    (v, f_env) = self.interpret(statement, f_env)
                return v
        elif callable(f):
            return f(*params)
        else:
            raise Exception(f, "Tried to call a non-function object")
