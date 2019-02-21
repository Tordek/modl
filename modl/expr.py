class TypedExpression():
    types = []


class Use():
    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return "USE " + repr(self.filename)


class Let():
    def __init__(self, assignments):
        self.assignments = assignments

    def __repr__(self):
        result = "LET "
        for name, value in assignments:
            result += repr(name) + " <- " + repr(value) + ", "
        return result


class Symchain(TypedExpression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return ("(" + repr(self.left) + ") " +
                repr(self.op) + " (" + repr(self.right) + ")")


class Identifier(TypedExpression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Typename():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Expression(TypedExpression):
    def __init__(self, call):
        self.call = call

    def __repr__(self):
        return repr(self.call)


class Grouping(TypedExpression):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return "(" + repr(self.expression) + ")"


class Function(TypedExpression):
    def __init__(self, args, body):
        self.args = args
        self.body = body

    def __repr__(self):
        return "Function {} of {} arguments".format(id(self), len(self.args))


class Literal(TypedExpression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


class Builtin(TypedExpression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '#' + self.name


class Conditional(TypedExpression):
    def __init__(self, cases):
        self.cases = cases

    def __repr__(self):
        result = "COND "
        result += "\n| ".join(repr(cond) + " -> " + repr(body)
                              for cond, body in self.cases)
        return result
