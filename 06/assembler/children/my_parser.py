"""parse mnemonic file (.asm) into binary file (.hack)
this version of the parser doesn't handle variables/symbols at all
"""


class Parser:
    """class to read through .asm file"""

    def __init__(self, inputFile):
        """open file and set-up variables"""
        asm = open(inputFile, 'r')
        self.asm = asm.read().split('\n')
        asm.close()
        self.idx = None
        self.command = None

    def reset(self):
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

    def command_type(self):
        """determines type of mnemonic command"""
        if self.command == '':
            return None
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
        if '=' in self.command:
            return self.command.split('=')[0]
        return ''

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
