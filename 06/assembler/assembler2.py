"""basic assembler
use parser and code modules to take a symbol-less
.asm file as input and output a .hack file
"""

from children.my_parser import Parser
from children.my_symbol_table import SymbolTable
import children.my_code as my_code

DIGITS = '0123456789'


def dec2bin(num):
    """convert number to binary"""
    if isinstance(num, str):
        num = int(num)
    return bin(num)[2:]


def zero_fill16(binary):
    """make a string length 16 by adding zeros"""
    temp = ['0'] * (16 - len(binary)) + [binary]
    return ''.join(temp)


def predefine_symbols(symbol_table):
    """add predefined symbols to the symbol table"""
    symbol_table.add_entry('SP', zero_fill16('0'))
    symbol_table.add_entry('LCL', zero_fill16('1'))
    symbol_table.add_entry('ARG', zero_fill16('10'))
    symbol_table.add_entry('THIS', zero_fill16('11'))
    symbol_table.add_entry('THAT', zero_fill16('100'))
    symbol_table.add_entry('SCREEN', zero_fill16(dec2bin(16384)))
    symbol_table.add_entry('KBD', zero_fill16(dec2bin(24576)))
    for i in range(16):
        symbol_table.add_entry('R' + str(i), zero_fill16(dec2bin(i)))


def setup_symbol_table(parse_file):
    """run through file once to assign instructions locations to symbols"""
    symbol_table = SymbolTable()
    predefine_symbols(symbol_table)
    instruction_address = 0
    while parse_file.has_more_commands():
        parse_file.advance()
        command_type = parse_file.command_type()
        if command_type == 'L_COMMAND':
            symbol = parse_file.symbol()
            symbol_table.add_entry(symbol, zero_fill16(
                dec2bin(instruction_address)))
        elif command_type:
            instruction_address += 1
    parse_file.reset()
    return symbol_table


def process_next_command(parse_file, hack_file, symbol_table, next_address):
    """called for each command in the file"""
    parse_file.advance()
    c_type = parse_file.command_type()
    if c_type is None:
        return

    elif c_type == 'A_COMMAND':
        symbol = parse_file.symbol()
        if symbol[0] in DIGITS:  # this is a number (not a symbol)
            command = zero_fill16(dec2bin(symbol))
        else:
            if symbol_table.contains(symbol):
                command = symbol_table.get_address(symbol)
            else:
                address = zero_fill16(dec2bin(next_address[0]))
                next_address[0] += 1
                symbol_table.add_entry(symbol, address)
                command = address

    elif c_type == 'L_COMMAND':
        return                              # no command generated

    elif c_type == 'C_COMMAND':
        command = '111' + my_code.comp(parse_file.comp()) + \
            my_code.dest(parse_file.destination()) + \
            my_code.jump(parse_file.jump())
    print(command)
    hack_file.write(command + '\n')


def assemble(file_base):
    """use parser class and supporting functions to read a file and write the binary file"""
    print('beginning')
    p = Parser(file_base + '.asm')
    b = open(file_base + '.hack', 'w')
    symbol_table = setup_symbol_table(p)
    next_address = [16]
    while p.has_more_commands():
        process_next_command(p, b, symbol_table, next_address)
    b.close()
    print('end')


# allow this file to be called from command line with argument for file
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print('no filename provided')
    else:
        F = sys.argv[1]
        if '.asm' in F:
            print('don\'t include .asm in the file base')
        else:
            assemble(F)
