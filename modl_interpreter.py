import modl_expr as expr
import modl_parser
import modl_scanner

class Builtin():
    def __init__(self, fun):
        self.fun = fun

BUILTIN = {}
BUILTIN['print'] = Builtin(lambda x: print(x))
BUILTIN['add'] = Builtin(lambda x, y: x + y)
BUILTIN['sub'] = Builtin(lambda x, y: x - y)
BUILTIN['read'] = Builtin(lambda: input())
BUILTIN['eq'] = Builtin(lambda x, y: x == y)
BUILTIN['gt'] = Builtin(lambda x, y: x > y)
BUILTIN['if'] = Builtin(lambda c, t, f: t if c else f)


class Environment():
    def __init__(self, parent=None):
        self.parent = parent
        self.contents = {}
        if self.parent is None:
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
            return statement.value
        elif isinstance(statement, expr.Expression):
            results = []
            for s in statement.call:
                results.append(self.interpret(s, environment))
            if len(results) == 1:
                return results[0]
            else:
                return self.do_call(*results)
        elif isinstance(statement, expr.Symchain):
            left = self.interpret(statement.left, environment)
            op = self.interpret(statement.op, environment)
            right = self.interpret(statement.right, environment)
            return self.do_call(op, left, right)
        elif isinstance(statement, expr.Use):
            with open(statement.identifier.name + ".dl") as file:
                contents = file.read()
                scanner = modl_scanner.Scanner(contents)
                parser = modl_parser.Parser(scanner.scan_tokens())
                for statement in parser.program():
                    self.interpret(statement, environment)
            return True
        elif isinstance(statement, expr.Let):
            name = statement.identifier.name
            value = self.interpret(statement.value, environment)            
            environment.set(name, value)
            return value
        elif isinstance(statement, expr.Identifier):
            return environment.get(statement.name)
        elif isinstance(statement, expr.Grouping):
            return self.interpret(statement.expression, environment)
        elif isinstance(statement, expr.Function):
            return Function(statement, environment)
        elif isinstance(statement, expr.Builtin):
            return BUILTIN[statement.name]

        
    def do_call(self, f, *params): # Supongo que funciona igual que haber hecho sin el zip, 1 por 1, pero es una optimizacion...
        if isinstance(f, Builtin):
            return f.fun(*params)
        else:            
            environment = Environment(f.environment)
            args = f.function.args
            for name, value in zip(args, params):
                environment.set(name.name, value)
            if len(args) > len(params):
                return Function(expr.Function(args[len(params):], f.function.body), environment)
            else:
                v = None
                for statement in f.function.body:
                    v = self.interpret(statement, environment)
                return v
