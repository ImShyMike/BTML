# SPDX-FileCopyrightText: 2025-present ShyMike <122023566+ImShyMike@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

import argparse
import sys

import uvicorn

from .parser import Parser
from .transpiler import transpile


def cli():
    """Command line interface for BTML."""
    parser = argparse.ArgumentParser(description="BTML - HTML but with curly brackets")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    transpile_parser = subparsers.add_parser("transpile", help="Transpile BTML to HTML")
    transpile_parser.add_argument("input", type=str, help="input BTML file")
    transpile_parser.add_argument(
        "-o", "--output", type=str, default=None, help="output HTML file"
    )

    server_parser = subparsers.add_parser("server", help="Start the BTML server")
    server_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)",
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )

    server_parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes to run (default: 1)",
    )

    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        default=None,
        help="input BTML file",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None, help="output HTML file"
    )

    args = parser.parse_args()

    if args.command == "server":
        print(f"Starting BTML server on {args.host}:{args.port}...", file=sys.stderr)
        uvicorn.run("btml.server:app", host=args.host, port=args.port, workers=args.workers)
        return

    if args.command == "transpile":
        input_file = args.input
    else:
        input_file = args.input

    if input_file is None:
        print("Error: No input file provided", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    if args.output is None:
        args.output = input_file.rsplit(".", 1)[0] + ".html"

    try:
        with open(input_file, "r", encoding="utf8") as file:
            btml_content = file.read()

        parser_instance = Parser()
        parsed_content = parser_instance.produce_ast(btml_content)
        html_output = transpile(parsed_content)

        with open(args.output, "w", encoding="utf8") as output_file:
            output_file.write(html_output)

        print(
            f'Successfully transpiled "{input_file}" to "{args.output}"',
            file=sys.stderr,
        )
    except FileNotFoundError:
        print(f'Error: Could not find input file "{input_file}"', file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error during transpilation: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Run the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
