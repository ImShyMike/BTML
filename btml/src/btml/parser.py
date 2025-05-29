"""Parser for BTML."""

from typing import List

from .btml_ast import (
    Attribute,
    Comment,
    Doctype,
    Expression,
    HTMLAttribute,
    Program,
    Statement,
    StringLiteral,
)
from .lexer import T, Token, tokenize


class Parser:
    """Parser for BTML source code."""

    def __init__(self):
        self.source_code = ""
        self.tokens = []

    def not_eof(self) -> bool:
        """Check if the end of file (EOF) has not been reached."""
        return len(self.tokens) > 0 and self.tokens[0].type != T.EOF

    def at(self) -> Token:
        """Get the current token."""
        return self.tokens[0]

    def next(self) -> Token:
        """Get the current token and skip to next one (also called eat)."""
        return self.tokens.pop(0)

    def look_ahead(self, n: int) -> Token:
        """Look ahead n tokens."""
        return self.tokens[n]

    def assert_next(self, token_type: T) -> Token:
        """Return the current token and assert that the next token is of a certain type."""
        token = self.next()
        if token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, but got {token.type}")
        return token

    def parse_comment(self) -> Comment:
        """Parse a comment from the source code."""
        if self.at().type == T.COMMENT:
            comment_token = self.next()
            return Comment(position=comment_token.position, content=comment_token.value)
        raise SyntaxError("Expected a comment token")

    def parse_attribute(self) -> Statement:
        """Parse an HTML attribute from the source code."""
        if self.at().type == T.IDENTIFIER:
            name = self.next().value

            position = self.at().position

            properties = []
            if self.at().type == T.OPEN_BRACKET:
                properties = self.parse_properties()

            current_token = self.at()

            if current_token.type == T.OPEN_BRACE:
                self.next()

                attribute_values = []
                while self.not_eof() and self.at().type != T.CLOSE_BRACE:
                    match self.at().type:
                        case T.STRING:
                            string_token = self.next()
                            attribute_values.append(
                                StringLiteral(
                                    position=string_token.position,
                                    value=string_token.value,
                                )
                            )
                        case T.COMMENT:
                            attribute_values.append(self.parse_comment())
                        case T.IDENTIFIER:
                            attribute_values.append(self.parse_attribute())
                        case _:
                            raise SyntaxError(
                                f"Expected attribute content, but got {self.at().type}"
                            )

                if self.at().type == T.CLOSE_BRACE:
                    self.next()
                else:
                    raise SyntaxError(
                        f"Expected closing brace, but got {self.at().type}"
                    )

                return HTMLAttribute(
                    position=position,
                    name=name,
                    value=attribute_values,
                    properties=properties,
                )

            if current_token.type == T.STRING:
                value = StringLiteral(
                    position=current_token.position, value=current_token.value
                )
                self.next()
                return HTMLAttribute(
                    position=position,
                    name=name,
                    value=[value],
                    properties=properties,
                )

            if current_token.type == T.DOT:
                self.next()
                return HTMLAttribute(
                    position=position,
                    name=name,
                    value=[],
                    properties=properties,
                    close=False,
                )

        raise SyntaxError("Expected identifier for attribute name")

    def parse_expression(self) -> Expression:
        """Parse an expression from the source code."""
        match self.at().type:
            case T.STRING:
                string_token = self.next()
                return StringLiteral(
                    position=string_token.position, value=string_token.value
                )
            case T.CLOSE_BRACE:
                raise SyntaxError("Unexpected closing brace")
            case _:
                raise SyntaxError(f"Unexpected token: {self.at().type}")

    def parse_properties(self) -> List[Attribute]:
        """Parse properties from the source code."""
        if self.at().type == T.OPEN_BRACKET:
            self.next()
            properties = []

            while self.not_eof() and self.at().type != T.CLOSE_BRACKET:
                properties.append(self.parse_property_value())

            if self.at().type == T.CLOSE_BRACKET:
                self.next()
            else:
                raise SyntaxError("Expected closing bracket")

            return properties

        raise SyntaxError("Expected opening bracket for properties")

    def parse_property_value(self) -> Attribute:
        """Parse a property value from the source code."""
        token = None
        if self.at().type in (T.IDENTIFIER, T.STRING):
            token = self.next()
        else:
            raise SyntaxError(
                f"Expected identifier or string, but got {self.at().type}"
            )

        if self.at().type == T.EQUALS:
            self.next()

            if self.at().type == T.STRING:
                value_token = self.next()
                return Attribute(
                    position=token.position,
                    name=token.value,
                    value=value_token.value,
                )

            if self.at().type == T.IDENTIFIER:
                value_token = self.next()
                return Attribute(
                    position=token.position,
                    name=token.value,
                    value=value_token.value,
                )

            raise SyntaxError(
                f"Expected string or identifier after '=', but got {self.at().type}"
            )

        return Attribute(position=token.position, name=token.value, value=None)

    def parse_doctype(self) -> Statement:
        """Parse a doctype declaration from the source code."""
        if self.at().type == T.EXCLAMATION:
            self.next()

        if self.at().type in (T.IDENTIFIER, T.STRING):
            name_token = self.next()
            self.assert_next(T.EXCLAMATION)
            return Doctype(position=name_token.position, value=name_token.value)

        raise SyntaxError("Expected doctype declaration")

    def parse_statement(self) -> Statement:
        """Parse a statement from the source code."""
        match self.at().type:
            case T.IDENTIFIER:
                return self.parse_attribute()
            case T.COMMENT:
                return self.parse_comment()
            case T.EXCLAMATION:
                return self.parse_doctype()
            case _:
                return self.parse_expression()

    def produce_ast(self, source_code: str) -> Program:
        """Produce the abstract syntax tree (AST) from the source code."""
        self.source_code = source_code
        self.tokens = tokenize(source_code)
        program = Program((0, 0, 0), body=[])

        while self.not_eof():
            statement = self.parse_statement()
            if statement != Expression((0, 0, 0)):
                program.body.append(statement)

        return program
