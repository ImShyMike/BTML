"""Transpiler that turns BTML into HTML."""

from typing import Sequence

from .btml_ast import (
    Attribute,
    Comment,
    Doctype,
    HTMLAttribute,
    Program,
    Statement,
    StringLiteral,
)

NO_EXPAND_TAGS = [
    "p",
    "h1",
    "h2",
    "div",
    "blockquote",
    "pre",
    "article",
    "section",
    "aside",
    "figcaption",
    "span",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "mark",
    "small",
    "sub",
    "sup",
    "code",
    "kbd",
    "samp",
    "var",
    "abbr",
    "cite",
    "q",
    "del",
    "ins",
    "li",
    "dd",
    "dt",
    "a",
    "label",
    "summary",
    "legend",
    "button",
    "title",
    "meta",
    "link",
]


def properties_to_string(properties: Sequence[Attribute]) -> str:
    """Convert properties to a string representation."""

    if not properties:
        return ""

    property_str = " " + " ".join(
        f'{prop.name}="{prop.value}"' if prop.value else prop.name
        for prop in properties
    )

    return property_str


def to_string(
    statements: Sequence[Statement],
    use_newline: bool = True,
    spaces: int = 2,
    n: int = 0,
) -> str:
    """Convert a statement to a string representation."""
    indent = ("\n" + (" " * spaces * n)) if use_newline else "" * spaces
    if not statements:
        return ""

    result = []
    for statement in statements:
        match statement:
            case Program():
                raise NotImplementedError(
                    "Program statements should not be directly converted to string."
                )
            case HTMLAttribute():
                result.append(
                    f"{indent}<{statement.name}{properties_to_string(statement.properties)}>"
                    + (
                        (
                            f"{
                                to_string(
                                    statement.value,
                                    use_newline=use_newline
                                    if statement.name not in NO_EXPAND_TAGS
                                    else False,
                                    spaces=spaces,
                                    n=n + (1 if statement.name != 'html' else 0),
                                )
                            }"
                            f"{indent if statement.name not in NO_EXPAND_TAGS else ''}</{statement.name}>"
                        )
                        if statement.close
                        else ""
                    )
                )
            case Comment():
                result.append(f"{indent}<!-- {statement.content} -->")
            case StringLiteral():
                result.append(f"{indent}{statement.value}")
            case Doctype():
                result.append(f"{indent}<!DOCTYPE {statement.value}>")
            case _:
                result.append(f"{indent}Unknown statement type")

    return "".join(result)


def transpile(program: Program):
    """Transpile the AST into target code."""

    transpiled = to_string(program.body, use_newline=True, spaces=2).strip()

    return transpiled
