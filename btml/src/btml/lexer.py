"""Lexer for BTML."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, List, Tuple


class T(Enum):
    """Token types for BTML."""

    EOF = auto()  # End of file

    IDENTIFIER = auto()  # Identifiers
    STRING = auto()  # Strings
    COMMENT = auto()  # Comments (e.g., <# comment #>)

    EQUALS = auto()  # Equals sign
    EXCLAMATION = auto()  # Exclamation mark
    DOT = auto()  # Dot (.)

    OPEN_BRACE = auto()  # Open brace
    CLOSE_BRACE = auto()  # Close brace
    OPEN_BRACKET = auto()  # Open bracket
    CLOSE_BRACKET = auto()  # Close bracket


TOKENS = {
    1: {  # Token size
        "{": T.OPEN_BRACE,  # Open brace
        "}": T.CLOSE_BRACE,  # Close brace
        "[": T.OPEN_BRACKET,  # Open bracket
        "]": T.CLOSE_BRACKET,  # Close bracket
        "=": T.EQUALS,  # Equals sign
        "!": T.EXCLAMATION,  # Exclamation mark
        ".": T.DOT,  # Dot
    }
}


@dataclass
class Token:
    """Represents a token in the BTML lexer."""

    value: Any
    type: T
    position: Tuple[int, int, int]  # (line, column, length)


def can_skip(string: str) -> bool:
    """Check if a token (as string) can be skipped."""
    return string in ("\n", "\r", " ", "\t")


def multi_pop(src: List[Any], n: int) -> List[Any]:
    """Pop multiple items from the source list."""
    popped = []
    for _ in range(n):
        if src:
            popped.append(src.pop(0))
    return popped


def tokenize(source: str) -> List[Token]:
    """Tokenize the source code."""

    src = list(source)
    token_output = []
    while src:
        # First, check for whitespace or newlines that can be skipped
        if can_skip(src[0]):
            src.pop(0)
            continue

        # Check for comments
        if src[:2] == ["<", "#"]:
            # Advance past the start of the comment
            multi_pop(src, 2)

            # Get the comment
            comment = ""
            while src and src[:2] != ["#", ">"]:
                comment += src.pop(0)

            # Advance past the end of the comment
            multi_pop(src, 2)

            token_output.append(
                Token(
                    value=comment,
                    type=T.COMMENT,
                    position=(1, 0, len(comment) + 4),
                )
            )
            continue

        # Check for tokens
        token_found = False
        for token_size, token_map in sorted(TOKENS.items(), reverse=True):
            token_value = "".join(src[:token_size])
            if token_value in token_map:
                token_type = token_map[token_value]
                position = (1, 0, len(token_value))
                token_output.append(
                    Token(value=token_value, type=token_type, position=position)
                )
                multi_pop(src, token_size)
                token_found = True
                break
        if token_found:
            continue

        # Check for identifiers
        if src[0].isalpha() or src[0] == "_":
            identifier = ""
            while src and (src[0].isalnum() or src[0] == "_"):
                identifier += src.pop(0)

            position = (1, 0, len(identifier))
            token_output.append(
                Token(value=identifier, type=T.IDENTIFIER, position=position)
            )
            continue

        # Check for string literals
        if src[0] in ('"', "'"):
            quote_type = src.pop(0)  # Get and remove the opening quote
            string = ""
            escaped = False

            while src:
                char = src.pop(0)
                if char == "" or (char == quote_type and not escaped):
                    break

                if escaped:
                    escaped = False
                    string += char
                elif char == "\\" and len(src) > 0 and src[0] in ('"', "'"):
                    escaped = True
                else:
                    string += char

            token_output.append(
                Token(
                    string,
                    T.STRING,
                    (1, 0, len(string) + 2),
                )
            )
            continue
        else:
            # Skip unknown character
            print(f"Warning: Skipping unknown character: {src.pop(0)}")

    # Add EOF token at the end
    token_output.append(Token(value=None, type=T.EOF, position=(1, 0, 0)))

    return token_output


if __name__ == "__main__":
    # Example usage
    CODE = 'test { key "value test" } <# This is a comment #>'
    tokens = tokenize(CODE)
    for token in tokens:
        print(f"Token: {token.value}, Type: {token.type}, Position: {token.position}")
