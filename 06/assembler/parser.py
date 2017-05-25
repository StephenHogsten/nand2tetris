"""parse mnemonic file (.asm) into binary file (.hack)
this version of the parser doesn't handle variables/symbols at all
"""
import re


class Parser:
    """file containing assembly code"""
    alpha = re.compile('[0-9a-zA-Z]+')

    def __init__(self, inputFile):
        """open file and set-up variables"""
        asm = open(inputFile, 'r')
        self.asm = asm.read().split('\n')
        asm.close()
        self.idx = None
        self.command = None

    def has_more_commands(self):
        """return bool for whether there are more lines with commands"""
        if self.idx is None:
            return bool(self.asm)
        return self.idx < len(self.asm) - 1

    def advance(self):
        """moves active commands down one line"""
        if self.idx is None:
            self.idx = 0
        else:
            self.idx += 1
        command = self.asm[self.idx].split('//')[0]
        self.command = ''.join(command.split(' '))
        print(self.command)

    def command_type(self):
        """determines type of mnemonic command"""
        if self.command[0] == '@':
            return 'A_COMMAND'
        elif self.command[0] == '(':
            return 'L_COMMAND'  # pseudo command
        return 'C_COMMAND'

    def symbol(self):
        """extracts symbol from A command"""
        symbol = self.command[1:]
        l = len(symbol) - 1
        if symbol[l] == ')':
            symbol = symbol[:l]
        return symbol

    def destination(self):
        """returns mnemonic for destination"""
        return self.command.split('=')[0]

    def comp(self):
        """returns caclulation component"""
        line = self.command
        if '=' in line:
            line = line.split('=')[1]
        if ';' in line:
            line = line.split(';')[0]
        return line

    def jump(self):
        """returns jump component (j1, j2, j3)"""
        line = self.command
        if ';' in line:
            return line.split(';')[1]
        return line


def dest(mnemonic):
    """translates destination mnemonic to binary"""
    res = ['0', '0', '0']
    if 'A' in mnemonic:
        res[0] = '1'
    if 'D' in mnemonic:
        res[1] = '1'
    if 'M' in mnemonic:
        res[2] = '1'
    return ''.join(res)


def comp(mnem):
    """parse calculation mnemonic"""
    if mnem == '0':
        ans = '0101010'
    elif mnem == '1':
        ans = '0111111'
    elif mnem == '-1':
        ans = '0111010'
    elif mnem == 'D':
        ans = '0001100'
    elif mnem == 'A':
        ans = '0110000'
    elif mnem == '!D':
        ans = '0001101'
    elif mnem == '!A':
        ans = '0110001'
    elif mnem == '-D':
        ans = '0001111'
    elif mnem == '-A':
        ans = '0110011'
    elif mnem == 'D+1':
        ans = '0011111'
    elif mnem == 'A+1':
        ans = '0110111'
    elif mnem == 'D-1':
        ans = '0001110'
    elif mnem == 'A-1':
        ans = '0110010'
    elif mnem == 'D+A':
        ans = '0000010'
    elif mnem == 'D-A':
        ans = '0010011'
    elif mnem == 'A-D':
        ans = '0000111'
    elif mnem == 'D&A':
        ans = '0000000'
    elif mnem == 'D|A':
        ans = '0010101'
    elif mnem == 'M':
        ans = '1110000'
    elif mnem == '!M':
        ans = '1110001'
    elif mnem == '-M':
        ans = '1110011'
    elif mnem == 'M+1':
        ans = '1110111'
    elif mnem == 'M-1':
        ans = '1110010'
    elif mnem == 'D+M':
        ans = '1000010'
    elif mnem == 'D-M':
        ans = '1010011'
    elif mnem == 'M-D':
        ans = '1000111'
    elif mnem == 'D&M':
        ans = '1000000'
    elif mnem == 'D|M':
        ans = '1010101'
    else:
        ans = 'error'
    return ans


def jump(mnem):
    """parse jump mnemonic"""
    if mnem == '':
        return '000'
    if mnem == 'JNE':
        return '101'
    if mnem == 'JMP':
        return '111'
    b = ['0'] * 3
    if 'E' in mnem:
        b[1] = '1'
    if 'G' in mnem:
        b[2] = '1'
    if 'L' in mnem:
        b[0] = '1'
    return ''.join(b)


def assemble(file_base):
    """use parser class and supporting functions to read a file and write the binary file"""
    p = Parser(file_base + '.asm')
    b = open(file_base + '.hack', 'w')
    while p.has_more_commands:
        p.advance()
        c = p.command_type()
        if c == 'A_COMMAND':
            command = '0' + p.symbol()
        elif c == 'L_COMMAND':
            print('L command - do nothing')
        elif c == 'C_COMMAND':
            command = dest(p.destination()) + comp(p.comp()) + jump(p.jump())
        b.write(command + '\n')
    b.close()


def print_file(test):
    """test reading/writing with python"""
    f = open(test, 'r')
    print(f.read())
    f.close()


# allow this file to be called from command line with argument for file
if __name__ == "__main__":
    import sys
    # assemble(sys.argv[1])
    print(sys.argv[1])
    # print_file(sys.argv[1])
