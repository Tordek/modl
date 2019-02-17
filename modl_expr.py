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
        return "(" + repr(self.left) + ") " + repr(self.op) + " (" + repr(self.right) + ")"
    
    
class Identifier(TypedExpression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Typename(TypedExpression):
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
    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __repr__(self):
        if self.type:
            return "[" + repr(self.type) + "] " + str(self.value)
        else:
            return repr(self.value)
    

class Builtin(TypedExpression):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '#' + self.name.lexeme

