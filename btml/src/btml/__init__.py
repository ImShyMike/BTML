# SPDX-FileCopyrightText: 2025-present ShyMike <122023566+ImShyMike@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT

import argparse
import sys
from .parser import Parser
from .transpiler import transpile

def cli():
    """Command line interface for BTML."""
    parser = argparse.ArgumentParser(description="BTML - HTML but with curly brackets")
    parser.add_argument("input", nargs="?", type=str, default=None, 
                       help="input BTML file")
    parser.add_argument("-o", "--output", type=str, default=None,
                       help="output HTML file")
    
    args = parser.parse_args()
    
    if args.input is None:
        print("Error: No input file provided", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
        
    if args.output is None:
        args.output = args.input.rsplit('.', 1)[0] + '.html'
        
    try:
        with open(args.input, 'r') as input_file:
            btml_content = input_file.read()
            
        parser_instance = Parser()
        parsed_content = parser_instance.produce_ast(btml_content)
        html_output = transpile(parsed_content)

        with open(args.output, 'w') as output_file:
            output_file.write(html_output)

        print(f"Successfully transpiled \"{args.input}\" to \"{args.output}\"", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: Could not find input file \"{args.input}\"", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during transpilation: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Run the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
