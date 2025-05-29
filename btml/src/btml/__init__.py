# SPDX-FileCopyrightText: 2025-present ShyMike <122023566+ImShyMike@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

from .parser import Parser
from .transpiler import transpile

def main():
    """Test function."""
    parser = Parser()
    code = """
!html!
html[lang="en"] {
    head {
        meta[charset="UTF-8"].
        title "My First Web Page"
    }
    body {
        h1 "Welcome to My Web Page"
        p "This is a simple HTML example with a button below."
        button[onclick="alert('Hello, world!')"] "Click Me"
    }
}"""
    ast = parser.produce_ast(code)
    print(transpile(ast))

if __name__ == "__main__":
    main()
