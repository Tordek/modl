class Use():
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return "USE " + repr(self.identifier)


class Let():
    def __init__(self, identifier, types, value):
        self.identifier = identifier
        self.types = types
        self.value = value

    def __repr__(self):
        if self.types:
            return "LET " + repr(self.identifier) + ": " + repr(self.types) +" <- " + repr(self.value)
        else:
            return "LET " + repr(self.identifier) + " <- " + repr(self.value)
        
        
class Symchain():
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return "(" + repr(self.left) + ") " + repr(self.op) + " (" + repr(self.right) + ")"
    
    
class Identifier():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Typename():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class Expression():
    def __init__(self, call):
        self.call = call

    def __repr__(self):
        return repr(self.call)
    
    
class Grouping():
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return "(" + repr(self.expression) + ")"
    

class Function():
    def __init__(self, args, body):
        self.args = args
        self.body = body

    def __repr__(self):
        return "Function {} of {} arguments".format(id(self), len(self.args))
    

class Literal():
    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __repr__(self):
        if self.type:
            return "[" + repr(self.type) + "] " + str(self.value)
        else:
            return repr(self.value)
    

class Builtin():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '#' + self.name.lexeme

