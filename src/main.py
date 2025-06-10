from lexer import tokenize
from parser import parse
from interpreter import run

code = open("trial.lava", "r").read();


tokens = tokenize(code)
ast = parse(tokens)
run(ast)
