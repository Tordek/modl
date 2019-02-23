class TypedExpression:
    types = []


class Use:
    def __init__(self, filename):
        self.filename = filename

    def __repr__(self):
        return "USE " + repr(self.filename)


class Let:
    def __init__(self, assignments):
        self.assignments = assignments

    def __repr__(self):
        return "(DEFINE " + '\n        '.join(repr(name) + " " + repr(value) for (name, value) in self.assignments) + ")"


class Symchain(TypedExpression):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return "(" + repr(self.op) + " " + repr(self.left) + " " + repr(self.right) + ")"


class Identifier(TypedExpression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Typename:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Expression(TypedExpression):
    def __init__(self, call):
        self.call = call

    def __repr__(self):
        return "(" + " ".join(repr(v) for v in self.call) + ")"


class Function(TypedExpression):
    def __init__(self, args, body):
        self.args = args
        self.body = body

    def __repr__(self):
        return "(LAMBDA (" + ' '.join(repr(arg) for arg in self.args) + ") " + ' '.join(repr(st) for st in self.body) + ")"


class Literal(TypedExpression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


class Builtin(TypedExpression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "#" + self.name


class Conditional(TypedExpression):
    def __init__(self, cases):
        self.cases = cases

    def __repr__(self):
        result = "(COND "
        for cond, body in self.cases:
            result += "("
            result += repr(cond)
            if len(body) == 1:
                result += " "
                result += repr(body[0])
            else:
                result += "(progn"
                for st in body:
                    result += "\n"
                    result += repr(st)
                result += ")"
            result += ") "
        result += ")"
        return result
