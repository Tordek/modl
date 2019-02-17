import enum

class TokenType(enum.Enum):
    # Single-Character tokens
    SEMICOLON = enum.auto()
    COLON = enum.auto()
    PIPE = enum.auto()
    BANG = enum.auto()
    COMMA = enum.auto()
    OPEN_BRACKETS = enum.auto()
    CLOSE_BRACKETS = enum.auto()
    OPEN_PARENTHESES = enum.auto()
    CLOSE_PARENTHESES = enum.auto()

    # Short tokens
    LEFT_ARROW = enum.auto()
    RIGHT_ARROW = enum.auto()
    COMMENT_START = enum.auto()
    COMMENT_END = enum.auto()
    EQUALS = enum.auto()

    # Symbol tokens
    SYMBOLIC = enum.auto() # Anything not beginning in [a-zA-Z0-9_]  that isn't above
    
    # Keywords
    USE = enum.auto()
    LET = enum.auto()

    # Literals
    IDENTIFIER = enum.auto() # [a-z][a-zA-Z0-9'-|]!?
    TYPENAME = enum.auto() # [A-Z][a-zA-Z0-9]
    STRING = enum.auto() # ".*"
    B10_INTEGER = enum.auto() # -?[0-9]+
    B10_FLOAT = enum.auto()
    BUILTIN = enum.auto()
    
    EOF = enum.auto()
    pass

class Token():
    def __init__(self, token_type, lexeme, literal, line):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
      
    def __repr__(self):
        if self.literal:
            return "{} '{}'".format(self.token_type, self.lexeme)
        else:
            return "{} '{}' {}".format(self.token_type, self.lexeme, self.literal)
