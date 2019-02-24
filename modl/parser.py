from . import expr
from .tokens import Token, TokenType


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def program(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.statement())
        return statements

    def statement(self):
        stmt = None
        if self.match(TokenType.USE):
            string = self.consume("Need a filename to import", TokenType.STRING)
            stmt = expr.Use(string.literal)
        elif self.match(TokenType.LET):
            stmt = self.let()
        else:
            stmt = self.symchain()
        self.consume("Expect ';' at end of statement.", TokenType.SEMICOLON)
        return stmt

    def let(self):
        assignments = []
        while True:
            identifier = None
            if self.match(TokenType.IDENTIFIER, TokenType.SYMBOLIC):
                # We only care about the name
                identifier = expr.Identifier(self.previous().lexeme)
            else:
                raise Exception(self.peek(), "Can't assign to this")

            self.consume("Missing <-", TokenType.LEFT_ARROW)
            value = self.symchain()
            assignments.append((identifier, value))
            if not self.match(TokenType.COMMA):
                break
        return expr.Let(assignments)

    def symchain(self):
        e = self.expression()

        while self.match(TokenType.SYMBOLIC):
            # We only care about the name
            symbol = expr.Identifier(self.previous().lexeme)
            right = self.symchain()
            e = expr.Symchain(e, symbol, right)

        return e

    def expression(self):
        chain = []

        while True:
            e = self.try_primary()
            if e is None:
                break
            chain.append(e)

        head = chain[0]
        # Special case for bang functions: Add an implicit ! if they're
        # the first in the call
        if isinstance(head, expr.Identifier) and head.name[-1] == "!":
            chain = [chain[0], expr.Identifier("!")] + chain[1:]

        if len(chain) == 1:
            return chain[0]
        else:
            return expr.Expression(chain)

    def try_primary(self):
        value = self.try_primary_()
        types = []
        if self.match(TokenType.COLON):
            t = self.consume("Expected a type after :", TokenType.TYPENAME)
            types.append(t.lexeme)

            while self.match(TokenType.RIGHT_ARROW):
                t = self.consume("Expected a type after ->", TokenType.TYPENAME)
                types.append(t.lexeme)
        if value:
            value.types = types
        return value

    def try_primary_(self):
        if self.match(TokenType.OPEN_BRACKETS):
            argument_list = []
            head_arg = self.consume(
                "Argument list cannot be empty", TokenType.BANG, TokenType.IDENTIFIER
            )
            argument_list.append(expr.Identifier(head_arg.lexeme))
            while self.match(TokenType.IDENTIFIER):
                argument_list.append(expr.Identifier(self.previous().lexeme))
            self.consume("Missing argument delimiter", TokenType.PIPE)
            body = [self.statement()]
            while not self.check(TokenType.CLOSE_BRACKETS):
                e = self.statement()
                body.append(e)
            self.consume("Unclosed function definition", TokenType.CLOSE_BRACKETS)
            return expr.Function(argument_list, body)
        elif self.match(TokenType.STRING, TokenType.B10_FLOAT, TokenType.B10_INTEGER):
            return expr.Literal(self.previous().literal)
        elif self.match(TokenType.IDENTIFIER):
            return expr.Identifier(self.previous().lexeme)
        elif self.match(TokenType.BUILTIN):
            return expr.Builtin(self.previous().literal)
        elif self.match(TokenType.OPEN_PARENTHESES):
            if self.check(TokenType.SYMBOLIC):
                symbol = self.match(TokenType.SYMBOLIC)
                identifier = expr.Identifier(self.previous().lexeme)
                self.consume(
                    "Symbol expressions can only contain a symbol",
                    TokenType.CLOSE_PARENTHESES,
                )
                return identifier
            e = self.symchain()
            self.consume("Missing closing parentheses", TokenType.CLOSE_PARENTHESES)
            return e
        elif self.match(TokenType.COND):
            cases = []
            while True:
                self.consume("Missing condition delimiter", TokenType.PIPE)
                condition = self.symchain()
                self.consume("Missing condition delimiter", TokenType.RIGHT_ARROW)

                body = [self.statement()]
                while not self.check(TokenType.PIPE, TokenType.END):
                    body.append(self.statement())
                cases.append((condition, body))

                if self.match(TokenType.END):
                    break

            return expr.Conditional(cases)
        else:
            return None

    def check(self, *types):
        if self.is_at_end():
            return False
        return self.peek().token_type in types

    def match(self, *types):
        if self.check(*types):
            self.advance()
            return True
        return False

    def consume(self, message, *types):
        if self.check(*types):
            return self.advance()

        raise Exception(self.peek(), message)

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]
