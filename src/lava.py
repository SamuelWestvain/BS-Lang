# lava.py

import sys
from lexer import tokenize
from parser import parse
from interpreter import run, Environment

def run_lava_file(filename, show_tokens=False, show_ast=False):
    with open(filename, 'r') as f:
        code = f.read()
    tokens = tokenize(code)
    if show_tokens:
        print("-> TOKENS:", tokens)
    ast = parse(tokens)
    if show_ast:
        print("-> AST:", ast)
    run(ast)

def repl():
    print("🔥 Welcome to the LAVA_SCRIPT REPL 🔥")
    print("Type 'skibidi' to exit.\n")

    # Create environment with built-in functions
    env = Environment()

    while True:
        try:
            line = input("-> ")
            if line.strip() == "skibidi":
                print("👋 Exiting REPL.")
                break

            tokens = tokenize(line)
            ast = parse(tokens)
            run(ast, env)

        except SyntaxError as se:
            print("-> Syntax Error:", se)
        except Exception as e:
            print("-> Error:", e)

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print("Usage: python lava.py [-token] [-ast] [-shell] <file.lava>")
        sys.exit(1)

    if "-shell" in args:
        repl()
    else:
        show_tokens = "-token" in args
        show_ast = "-ast" in args
        filename = [arg for arg in args if arg.endswith(".lava")]

        if not filename:
            print("Error: No .lava file provided.")
            sys.exit(1)

        run_lava_file(filename[0], show_tokens, show_ast)