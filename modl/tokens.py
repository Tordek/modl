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
    COND = enum.auto()

    # Short tokens
    LEFT_ARROW = enum.auto()
    RIGHT_ARROW = enum.auto()
    COMMENT_START = enum.auto()
    COMMENT_END = enum.auto()
    EQUALS = enum.auto()

    # Symbol tokens, anything not beginning in isalpha() that isn't above
    SYMBOLIC = enum.auto()

    # Keywords
    USE = enum.auto()
    LET = enum.auto()

    # Literals
    IDENTIFIER = enum.auto()  # !isupper()[isalpha()'_|]+!?
    TYPENAME = enum.auto()  # isupper()(isalpha'_|)+
    STRING = enum.auto()  # ".*"
    B10_INTEGER = enum.auto()
    B10_FLOAT = enum.auto()
    BUILTIN = enum.auto()

    EOF = enum.auto()
    pass


class Token:
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
