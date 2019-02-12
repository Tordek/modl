import modl_expr as expr
from modl_tokens import Token, TokenType

class Parser():
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
            identifier = self.identifier()
            stmt = expr.Use(identifier)
        elif self.match(TokenType.LET):
            identifier = None
            if self.match(TokenType.IDENTIFIER, TokenType.SYMBOLIC):
                identifier = expr.Identifier(self.previous().lexeme) # We only care about the name
            else:
                raise Exception(self.peek(), "Can't assign to this")
            
            types = []
            if self.match(TokenType.COLON):
                t = self.consume("Expected a type after :", TokenType.TYPENAME)
                types.append(t.lexeme)
                    
                while self.match(TokenType.RIGHT_ARROW):
                    t = self.consume("Expected a type after ->", TokenType.TYPENAME)
                    types.append(t.lexeme)
                    
            self.consume("Missing <-", TokenType.LEFT_ARROW)
            symchain = self.symchain()
            stmt = expr.Let(identifier, types, symchain)
        else:
            stmt = self.symchain()
        self.consume("Expect ';' at end of statement.", TokenType.SEMICOLON)
        return stmt

    def symchain(self):
        e = self.expression()

        while self.match(TokenType.SYMBOLIC):
            symbol = expr.Identifier(self.previous().lexeme) # We only care about the name
            right = self.symchain()
            e = expr.Symchain(e, symbol, right)

        return e

    def identifier(self):
        identifier = self.consume("Expected an identifier", TokenType.IDENTIFIER)
        return expr.Identifier(identifier.lexeme) # NAME

    def expression(self):
        chain = []

        while True:
            e = self.try_primary()
            if e is None:
                if self.match(TokenType.BANG):
                    chain.append(expr.Identifier(self.previous().lexeme))
                else:
                    break
            chain.append(e)
        return expr.Expression(chain)

    def primary(self):
        result = self.try_primary()
        if result is None:
            raise Exception(self.peek(), "Unknown symbol")
        return result
    
    def try_primary(self):    
        if self.match(TokenType.OPEN_BRACKETS):
            argument_list = []
            head_arg = self.consume("Argument list cannot be empty", TokenType.BANG, TokenType.IDENTIFIER)
            argument_list.append(expr.Identifier(head_arg.lexeme))
            while self.match(TokenType.IDENTIFIER):
                argument_list.append(expr.Identifier(self.previous().lexeme))
            self.consume("Missing argument delimiter", TokenType.PIPE);
            body = []        
            while not self.check(TokenType.CLOSE_BRACKETS):
                e = self.statement()
                body.append(e)
            self.consume("Unclosed function definition", TokenType.CLOSE_BRACKETS)
            return expr.Function(argument_list, body)
        elif self.match(TokenType.STRING, TokenType.B10_FLOAT, TokenType.B10_INTEGER):
            return expr.Literal(self.previous().literal, None) # Type?
        elif self.match(TokenType.IDENTIFIER):
            return expr.Identifier(self.previous().lexeme)
        elif self.match(TokenType.BUILTIN):
            return expr.Builtin(self.previous().lexeme)
        elif self.match(TokenType.OPEN_PARENTHESES):
            e = self.symchain()
            self.consume("Missing closing parentheses", TokenType.CLOSE_PARENTHESES)
            return expr.Grouping(e)
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
