import collections
import modl_expr as expr
import modl_parser
import modl_scanner

BUILTIN = {
    'print': lambda x: print(x),
    'add': lambda x, y: x + y,
    'sub': lambda x, y: x - y,
    'read': lambda: input(),
    'eq': lambda x, y: x == y,
    'gt': lambda x, y: x > y,
    'if': lambda c, t, f: t if c else f,
}


class Environment():
    def __init__(self, parent=None):
        self.contents = parent or collections.ChainMap()
        self.is_frozen = False
        
    def get(self, name):
        return self.contents[name]

    def set(self, name, value):
        if self.is_frozen:
            env = Environment(self.contents.new_child())
        else:
            env = self

        env.contents[name] = value
        return env

    def freeze(self):
        self.is_frozen = True
        

class Function():
    def __init__(self, function, environment):
        self.function = function
        self.environment = environment

        
class Interpreter():
    def interpret(self, statement, environment):
        if isinstance(statement, expr.Literal):
            return (statement.value, environment)
        elif isinstance(statement, expr.Expression):
            results = []
            for s in statement.call:
                result, environment = self.interpret(s, environment)
                results.append(result)
            if len(results) == 1:
                return (results[0], environment)
            else:
                return self.do_call(*results, environment=environment)
        elif isinstance(statement, expr.Symchain):
            (left, environment) = self.interpret(statement.left, environment)
            (op, environment) = self.interpret(statement.op, environment)
            (right, environment) = self.interpret(statement.right, environment)
            return self.do_call(op, left, right, environment=environment)
        elif isinstance(statement, expr.Use):
            with open(statement.identifier.name + ".dl") as file:
                contents = file.read()
                scanner = modl_scanner.Scanner(contents)
                parser = modl_parser.Parser(scanner.scan_tokens())
                for statement in parser.program():
                    _, environment = self.interpret(statement, environment)
            return (True, environment)
        elif isinstance(statement, expr.Let):
            name = statement.identifier.name
            (value, environment) = self.interpret(statement.value, environment)            
            environment = environment.set(name, value)
            return (value, environment)
        elif isinstance(statement, expr.Identifier):
            return (environment.get(statement.name), environment)
        elif isinstance(statement, expr.Grouping):
            return self.interpret(statement.expression, environment)
        elif isinstance(statement, expr.Function):
            environment.freeze()
            return (Function(statement, environment), environment)
        elif isinstance(statement, expr.Builtin):
            return (BUILTIN[statement.name], environment)
        else:
            raise Exception("Trying to run unknown thing", statement)

        
    def do_call(self, f, *params, environment): # Supongo que funciona igual que haber hecho sin el zip, 1 por 1, pero es una optimizacion...
        if isinstance(f, Function):
            f_environment = f.environment
            args = f.function.args
            for name, value in zip(args, params):
                f_environment = f_environment.set(name.name, value)
            if len(args) > len(params):
                return (Function(expr.Function(args[len(params):], f.function.body), f_environment), environment)
            else:
                v = None
                for statement in f.function.body:
                    (v, f_environment) = self.interpret(statement, f_environment)
                return (v, environment)
        else:            
            return (f(*params), environment)
