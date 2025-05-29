"""AST (Abstract Syntax Tree) for BTML."""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Statement:
    """Base class for all statements in the AST."""

    # Used for errors, structure is (line, column, length)
    position: Tuple[int, int, int]


@dataclass
class Expression(Statement):
    """Base class for all expressions in the AST."""

    # Same position as Statement
    position: Tuple[int, int, int]


# -- Statements --


@dataclass
class Program(Statement):
    """Represents a complete BTML program."""

    body: List[Statement] = field(default_factory=list)


@dataclass
class Attribute(Statement):
    """Represents an attribute in a BTML statement."""

    name: str
    value: str | None = None


@dataclass
class HTMLAttribute(Statement):
    """Represents an HTML attribute in a BTML statement."""

    name: str
    value: List[Expression]
    properties: List[Attribute] = field(default_factory=list)
    close: bool = True


@dataclass
class Comment(Statement):
    """Represents a comment in the BTML source code."""

    content: str


@dataclass
class Doctype(Statement):
    """Represents a doctype declaration in the BTML source code."""

    value: str


# -- Expressions --


@dataclass
class StringLiteral(Expression):
    """Represents a string literal."""

    value: str
