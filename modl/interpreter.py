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


class TailCall:
    def __init__(self, f, params):
        self.f = f
        self.params = params


def interpret(statement, environment, is_tail_call=False):
    if isinstance(statement, expr.Literal):
        return (statement.value, environment)
    elif isinstance(statement, expr.Identifier):
        return (environment[statement.name], environment)
    elif isinstance(statement, expr.Grouping):
        return interpret(statement.expression, environment)
    elif isinstance(statement, expr.Function):
        return (Function(statement, environment), environment)
    elif isinstance(statement, expr.Builtin):
        return (BUILTIN[statement.name], environment)
    elif isinstance(statement, expr.Use):
        with open(statement.filename) as file:
            contents = file.read()
            scanner = Scanner(contents)
            parser = Parser(scanner.scan_tokens())
            for statement in parser.program():
                result, environment = interpret(statement, environment)
            return (result, environment)
    elif isinstance(statement, expr.Let):
        environment = environment.new_child()
        for (name, value) in statement.assignments:
            (evaluated_value, _) = interpret(value, environment)
            environment[name.name] = evaluated_value
        return (None, environment)
    elif isinstance(statement, expr.Expression):
        results = []
        for s in statement.call:
            result, _ = interpret(s, environment)
            results.append(result)
        if is_tail_call:
            return TailCall(results[0], results[1:])
        else:
            return (do_call(*results), environment)
    elif isinstance(statement, expr.Symchain):
        (left, _) = interpret(statement.left, environment)
        (op, _) = interpret(statement.op, environment)
        (right, _) = interpret(statement.right, environment)
        if is_tail_call:
            return TailCall(op, [left, right])
        else:
            return (do_call(op, left, right), environment)
    elif isinstance(statement, expr.Conditional):
        # Discard the environment from the evaluation
        # to disallow `let`s done inside a case
        for condition, body in statement.cases:
            value, _ = interpret(condition, environment)
            if value is True:
                env = environment
                if is_tail_call:
                    for st in body[:-1]:
                        result, env = interpret(st, env)
                    return interpret(body[-1], env, True)
                else:
                    for st in body:
                        result, env = interpret(st, env)
                    return result, environment
            elif value is False:
                continue
            else:
                raise Exception("Type mismatch, condition must be boolean", value)
    else:
        raise Exception("Trying to run unknown thing", statement)


def do_call(f, *params):
    while True:
        # Currying, but optimized if there are multiple parameters
        if isinstance(f, Function):
            f_env = f.environment.new_child()
            args = f.function.args
            for name, value in zip(args, params):
                f_env[name.name] = value
            if len(args) > len(params):
                return Function(
                    expr.Function(args[len(params) :], f.function.body), f_env
                )
            else:
                v = None
                for statement in f.function.body[:-1]:
                    (v, f_env) = interpret(statement, f_env)
                result = interpret(f.function.body[-1], f_env, True)
                if isinstance(result, TailCall):
                    f = result.f
                    params = result.params
                    continue
                else:
                    return result[0]
        elif callable(f):
            return f(*params)
        else:
            raise Exception(f, "Tried to call a non-function object")
