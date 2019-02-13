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
        self.parent = parent
        self.contents = {}
        self.contents['!'] = '!'
        
    def get(self, name):
        if name in self.contents:
            return self.contents[name]

        if self.parent is None or name == '!':
            raise Exception("Couldn't find symbol", name)

        return self.parent.get(name);

    def set(self, name, value):
        try:
            self.get(name)
            raise Exception("Symbol already set", name, self.get(name))
        except:
            self.contents[name] = value
        

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
            left = self.interpret(statement.left, environment)
            op = self.interpret(statement.op, environment)
            right = self.interpret(statement.right, environment)
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
            environment = Environment(environment) # Tree building!
            environment.set(name, value) # TODO: Since nothing gets updated, this should just be part of environment creation.
            return (value, environment)
        elif isinstance(statement, expr.Identifier):
            return (environment.get(statement.name), environment)
        elif isinstance(statement, expr.Grouping):
            return self.interpret(statement.expression, environment)
        elif isinstance(statement, expr.Function):
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
                f_environment.set(name.name, value)
            if len(args) > len(params):
                return (Function(expr.Function(args[len(params):], f.function.body), f_environment), environment)
            else:
                v = None
                for statement in f.function.body:
                    (v, f_environment) = self.interpret(statement, f_environment)
                return (v, environment)
        else:            
            return (f(*params), environment)
