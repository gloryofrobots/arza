# TODO MOVE IT TO LEXER / PARSER
from obin.misc.platform import re

num_lit_exp = r'(?:[+-]?((?:(?:\d+)(?:\.\d*)?)|Infinity|(?:\.[0-9]+))(?:[eE][\+\-]?[0-9]*)?)'
num_lit_rexp = re.compile(num_lit_exp)
num_rexp = re.compile(r'^%s$' % num_lit_exp)
hex_rexp = re.compile(r'^0[xX]([\dA-Fa-f]+)$')
oct_rexp = re.compile(r'^0([0-7]+)$')

