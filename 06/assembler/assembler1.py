"""basic assembler
use parser and code modules to take a symbol-less
.asm file as input and output a .hack file
"""

from children.my_parser import Parser
from children.my_code import comp, dest, jump


def assemble(file_base):
    """use parser class and supporting functions to read a file and write the binary file"""
    print('beginning')
    p = Parser(file_base + '.asm')
    b = open(file_base + '.hack', 'w')
    commands = []
    while p.has_more_commands():
        p.advance()
        c = p.command_type()
        if c is None:
            continue
        elif c == 'A_COMMAND':
            symb = bin(int(p.symbol()))[2:]
            zeros = ['0'] * (16 - len(symb))
            command = ''.join(zeros) + symb
        elif c == 'L_COMMAND':
            print('L command - do nothing')
        elif c == 'C_COMMAND':
            command = '111' + comp(p.comp()) + \
                dest(p.destination()) + jump(p.jump())
        b.write(command + '\n')
        commands.append(command)
    b.close()
    print('\n'.join(commands))
    print('end')


def print_file(test):
    """test reading/writing with python"""
    f = open(test, 'r')
    print(f.read())
    f.close()


# allow this file to be called from command line with argument for file
if __name__ == "__main__":
    import sys
    import os.path
    if len(sys.argv) < 2:
        print('no filename provided')
    else:
        F = sys.argv[1]
        print('isfile? ', os.path.isfile(F))
        # F = '../add/Add'
        assemble(F)
        # print(sys.argv[1])
        # print_file(sys.argv[1])
