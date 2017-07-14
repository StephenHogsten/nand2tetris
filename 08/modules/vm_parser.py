"""module for the class that parser the .vm file"""

COMMAND_DICT = {
    'pop': 'C_POP',
    'push': 'C_PUSH',
    'label': 'C_LABEL',
    'goto': 'C_GOTO',
    'if-goto': 'C_IF',
    'function': 'C_FUNCTION',
    'call': 'C_CALL',
    'return': 'C_RETURN',
    'add': 'C_ARITHMETIC',
    'sub': 'C_ARITHMETIC',
    'neg': 'C_ARITHMETIC',
    'eq': 'C_ARITHMETIC',
    'gt': 'C_ARITHMETIC',
    'lt': 'C_ARITHMETIC',
    'and': 'C_ARITHMETIC',
    'or': 'C_ARITHMETIC',
    'not': 'C_ARITHMETIC'
}


class Parser:
    """parses a .vm file"""

    def __init__(self, filename):
        """open file and set-up variables"""
        print('filename2', filename)
        f = open(filename, 'r')
        lines = [line.split('//')[0].strip() for line in f.read().split('\n')]
        f.close()

        self.lines = [line for line in lines if line != '']
        self.next_line = 0
        self.command = None

    def has_more_commands(self):
        """returns bool if there's a next line"""
        return self.next_line < len(self.lines)

    def advance(self, is_printing):
        """set command to next command"""
        self.command = self.lines[self.next_line]
        if is_printing:
            print(self.command)
        self.next_line += 1

    def command_type(self):
        """parse the VM command type"""
        command = self.command.split(' ')[0]
        if command in COMMAND_DICT:
            return COMMAND_DICT[command]
        return 'INVALID COMMAND TYPE'

    def arg1(self):
        """parse the first argument
        if it's C_ARITHMETIC return the operation"""
        if self.command_type() == 'C_ARITHMETIC':
            return self.command.split(' ')[0]
        return self.command.split(' ')[1]

    def arg2(self):
        """parse the second argument"""
        return self.command.split(' ')[2]
