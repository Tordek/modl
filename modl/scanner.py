from .tokens import Token, TokenType


class Scanner:
    # These tokens may not appear as part of a longer token
    unique_tokens = {
        ";": TokenType.SEMICOLON,
        "{": TokenType.OPEN_BRACKETS,
        "}": TokenType.CLOSE_BRACKETS,
        "(": TokenType.OPEN_PARENTHESES,
        ")": TokenType.CLOSE_PARENTHESES,
        ",": TokenType.COMMA,
    }

    # These tokens are reserved, but may appear as part of a longer token.
    reserved_symbols = {
        "->": TokenType.RIGHT_ARROW,
        "<-": TokenType.LEFT_ARROW,
        "!": TokenType.BANG,
        "|": TokenType.PIPE,
        ":": TokenType.COLON,
    }

    reserved_words = {
        "use": TokenType.USE,
        "let": TokenType.LET,
        "end": TokenType.END,
        "cond": TokenType.COND,
    }

    def __init__(self, source):
        self.source = source

        self.start = 0
        self.current = 0
        self.line = 1
        self.tokens = []

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_token(self):
        c = self.peek()
        if self.match("{#"):
            self.builtin()
        elif self.match("/*"):
            self.comment()
        elif c in self.unique_tokens:
            self.advance()
            self.add_token(self.unique_tokens[c])
        elif c in ["-", "."] or c.isnumeric():
            self.number()
        elif self.match("\n"):
            self.line += 1
        elif c.isspace():
            self.advance()
        elif self.match('"'):
            self.string()
        elif c.isupper():
            self.typename()
        elif c.isalpha():
            self.identifier()
        else:
            # All other characters count as symbols
            self.symbolic()

    def builtin(self):
        while self.valid_in_identifier(self.peek()):
            self.advance()
        if not self.match("}"):
            raise Exception(self.line, "Unterminated builtin literal")
        self.add_token(TokenType.BUILTIN, self.current_lexeme()[2:-1])

    def number(self):
        self.match("-")  # May match a starting -
        self.match(".")  # May match .??? or -.???

        is_number = False
        while True:
            c = self.peek()
            if c is None:
                break
            elif c.isnumeric():
                self.advance()
                is_number = True
            elif c == ".":
                self.advance()
            else:
                break

        if not is_number:
            return self.symbolic()

        if "." in self.current_lexeme():
            self.add_token(TokenType.B10_FLOAT, float(self.current_lexeme()))
        else:
            self.add_token(TokenType.B10_INTEGER, int(self.current_lexeme(), 10))

    def typename(self):
        while self.valid_in_identifier(self.peek()):
            self.advance()

        self.add_token(TokenType.TYPENAME)

    def identifier(self):
        while self.valid_in_identifier(self.peek()):
            self.advance()

        lexeme = self.current_lexeme()
        if lexeme in self.reserved_words:
            if self.match("!"):
                raise Exception("Can't use bangs after reserved words.")
            self.add_token(self.reserved_words[lexeme])
        else:
            self.match("!")
            self.add_token(TokenType.IDENTIFIER)

    def valid_in_identifier(self, c):
        if c is None:
            return False
        if c.isalnum():
            return True
        if c in "'_":
            return True
        return False

    def symbolic(self):
        while self.valid_as_symbolic(self.peek()):
            self.advance()
        lexeme = self.current_lexeme()
        if lexeme == "*/":
            raise Exception(self.line, "Unopened comment.")
        elif lexeme in self.reserved_symbols:
            self.add_token(self.reserved_symbols[lexeme])
        else:
            self.add_token(TokenType.SYMBOLIC)

    def valid_as_symbolic(self, c):
        if c is None:
            return False
        elif c.isspace():
            return False
        elif c.isalnum():
            return False
        elif c in self.unique_tokens:
            return False
        else:
            return True

    def string(self):
        literal = ""
        while self.peek() != '"' and not self.is_at_end():
            c = self.peek()  # Sure would like to have the walrus op
            if c == "\n":
                self.line += 1

            if c == "\\":  # Escape characters
                self.advance()
                if self.is_at_end():
                    break
                e = self.peek()
                if e == "n":
                    literal += "\n"
                elif e == "r":
                    literal += "\r"
                elif e == "t":
                    literal += "\t"
                elif e == "\\":
                    literal += "\\"
                elif e == '"':
                    literal += '"'
                elif e == "x":
                    # fetch 4 characters as hex and decode as unicode
                    codepoint = self.source[self.current + 1 : self.current + 5]
                    if len(codepoint) < 4:
                        raise Exception(self.line, "Unterminated string")
                    literal += chr(int(codepoint, 16))
                    self.current += 4
                else:
                    raise Exception(self.line, "\\" + e + " is not an escape sequence")
            else:
                literal += c
            self.advance()

        if self.is_at_end():
            raise Exception(self.line, "Unterminated string")

        self.advance()  # Closing "

        self.add_token(TokenType.STRING, literal)

    def comment(self):
        while not self.match("*/"):
            if self.is_at_end():
                raise Exception(self.line, "Unterminated comment")
            if self.peek() == "\n":
                self.line += 1
            self.advance()


        # self.add_token(TokenType.COMMENT, self.current_lexeme())

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def peek(self, n=1):
        if self.current + n > len(self.source):
            return None
        return self.source[self.current : self.current + n]

    def current_lexeme(self):
        return self.source[self.start : self.current]

    def add_token(self, token_type, literal=None):
        self.tokens.append(Token(token_type, self.current_lexeme(), literal, self.line))

    def match(self, c):
        if self.is_at_end():
            return False
        if self.peek(len(c)) != c:
            return False
        self.current += len(c)
        return True
