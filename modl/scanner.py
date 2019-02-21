from .tokens import Token, TokenType


class Scanner():
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
        c = self.advance()
        if c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '(':
            self.add_token(TokenType.OPEN_PARENTHESES)
        elif c == ')':
            self.add_token(TokenType.CLOSE_PARENTHESES)
        elif c == '!':
            self.add_token(TokenType.BANG)
        elif c == '{':
            if self.match('#'):
                self.identifier()
                self.match('}')
                builtin = self.tokens.pop()
                self.tokens.append(Token(TokenType.BUILTIN,
                                         builtin.lexeme[2:], None, self.line))
            else:
                self.add_token(TokenType.OPEN_BRACKETS)
        elif c == '}':
            self.add_token(TokenType.CLOSE_BRACKETS)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '/':
            if self.match('*'):
                self.comment()
            else:
                self.symbolic()
        elif c == '<':
            if self.match('-'):
                self.add_token(TokenType.LEFT_ARROW)
            else:
                self.symbolic()
        elif c == '-':
            if self.match('>'):
                self.add_token(TokenType.RIGHT_ARROW)
            elif self.peek().isnumeric() or self.peek() == '.':
                self.number()
            else:
                self.symbolic()
        elif c == '.':
            if self.peek().isnumeric() or self.peek() == '.':
                self.number()
            else:
                self.symbolic()
        elif c.isspace():
            return
        elif c == '\n':
            self.line += 1
            return
        elif c == '"':
            self.string()
        elif c.isnumeric():
            self.number()
        elif c.isalpha():
            self.identifier()
        else:
            # All other characters count as symbols
            self.symbolic()

    def number(self):
        c = self.source[self.current - 1]
        if c == '-':
            p = self.peek()
            if p is None:
                self.symbolic()
                return
            elif p in ' \r\t\n':
                pass
            elif p == '.' or p.isnumeric():  # -.5 is valid, -5 is, too.
                self.advance()
            else:
                self.symbolic()  # -' is not
                return

        c = self.source[self.current - 1]
        if c == '.':
            p = self.peek()
            if p is None:  # -. and . aren't numbers
                self.symbolic()
                return
            elif p in ' \r\t\n':
                pass
            elif p.isnumeric():
                self.advance()
            else:
                self.symbolic()
                return
        if not self.source[self.current-1].isnumeric():
            c = self.peek()
            if c is None or c in ' \r\t\n':
                pass
            elif c == '.' or c.isnumeric():
                pass
            else:
                self.symbolic()  # -.- is not a number
                return

        is_decimal = False
        while True:
            c = self.peek()
            if c is None or c in ' \r\t\n':
                break
            if c.isnumeric():
                self.advance()
            elif c == '.':
                if is_decimal:
                    raise Exception(self.line, "Wrong number literal")
                    return
                is_decimal = True
                self.advance()
            else:
                break

        if is_decimal:
            self.add_token(TokenType.B10_FLOAT, float(self.current_lexeme()))
        else:
            self.add_token(TokenType.B10_INTEGER,
                           int(self.current_lexeme(), 10))

    def identifier(self):
        while self.valid_in_identifier(self.peek()):
            self.advance()

        lexeme = self.current_lexeme()
        if lexeme == 'use':
            self.add_token(TokenType.USE)
        elif lexeme == 'let':
            self.add_token(TokenType.LET)
        elif lexeme == 'end':
            self.add_token(TokenType.END)
        elif lexeme == 'cond':
            self.add_token(TokenType.COND)
        else:
            self.match('!')  # Optional ending bang
            if lexeme[0].isupper():
                self.add_token(TokenType.TYPENAME)
            else:
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
        if lexeme == ':':
            self.add_token(TokenType.COLON)
        elif lexeme == '|':
            self.add_token(TokenType.PIPE)
        else:
            self.add_token(TokenType.SYMBOLIC)

    def valid_as_symbolic(self, c):
        if c is None:
            return False
        elif c.isspace():
            return False
        elif c.isalnum():
            return False
        elif c in "!(){},":
            return False
        else:
            return True

    def string(self):
        literal = ""
        while self.peek() != '"' and not self.is_at_end():
            c = self.peek()  # Sure would like to have the walrus op
            if c == '\n':
                self.line += 1

            if c == '\\':  # Escape characters
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
                elif e == "\"":
                    literal += "\""
                elif e == "x":
                    # fetch 4 characters as hex and decode as unicode
                    codepoint = self.source[self.current+1:self.current+5]
                    if len(codepoint) < 4:
                        raise Exception(self.line, "Unterminated string")
                    literal += chr(int(codepoint, 16))
                    self.current += 4
                else:
                    raise Exception(self.line,
                                    "\\" + e + " is not an escape sequence")
            else:
                literal += c
            self.advance()

        if self.is_at_end():
            raise Exception(self.line, "Unterminated string")
            return

        self.advance()  # Closing "

        self.add_token(TokenType.STRING, literal)

    def comment(self):
        while not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            elif self.peek() == '*' and self.peeknext() == '/':
                self.advance()
                self.advance()
                break
            self.advance()

            if self.is_at_end():
                raise Exception(self.line, "Unterminated comment")

        # self.add_token(TokenType.COMMENT, self.current_lexeme())

    def advance(self):
        self.current += 1
        return self.source[self.current-1]

    def peek(self):
        if self.is_at_end():
            return None
        return self.source[self.current]

    def peeknext(self):
        if self.current + 1 >= len(self.source):
            return None
        return self.source[self.current+1]

    def current_lexeme(self):
        return self.source[self.start:self.current]

    def add_token(self, token_type, literal=None):
        self.tokens.append(
            Token(token_type, self.current_lexeme(), literal, self.line)
        )

    def match(self, c):
        if self.is_at_end():
            return False
        if self.source[self.current] != c:
            return False
        self.current += 1
        return True
