"""module for a class that writes the .asm file"""

SEGMENT_DICT = {
    'local': 'LCL',
    'argument': 'ARG',
    'this': 'THIS',
    'that': 'THAT'
}


class Writer:
    """creates and writes an asm file"""

    def __init__(self):
        """initialize"""
        self.file = None
        self.dummy_idx = 0

    def line(self, command):
        """shortcut for appending a new line of text"""
        self.file.write(command)
        self.file.write('\n')

    def set_filename(self, filename):
        """opens file with specified name"""
        self.file = open(filename + '.asm', 'w')

    def close(self):
        """close output file"""
        self.file.close()

    def write_arithmetic(self, command):
        """takes VM code and outputs asm code to file"""
        self.line('// ' + command)      # for easier debugging
        if command in ('not', 'neg'):
            # unary
            self.line('@SP')
            # M is now the stop of the stack value
            self.line('A=M-1')
            if command == 'not':
                self.line('M=!M')
            else:                       # command is neg
                self.line('M=-M')
        else:
            # set D and M to 1st and 2nd places on the stack
            self.line('@SP')
            self.line('A=M-1')
            self.line('D=M')      # set D to top of the stack
            self.line('@SP')
            self.line('M=M-1')   # decrement top stack position
            self.line('A=M-1')   # M is new top of stack
            if command == 'add':
                self.line('M=D+M')
            elif command == 'sub':
                self.line('M=M-D')
            elif command == 'and':
                self.line('M=D&M')
            elif command == 'or':
                self.line('M=D|M')
            elif command in ('eq', 'gt', 'lt'):
                self.comparison_helper(command)
            else:
                print('error on command [' + command + ']')

    def comparison_helper(self, command):
        """writes asm code for eq, gt, lt arithemtic operations"""
        self.line('D=M-D')
        self.line('M=-1')
        self.line('@DUMMY' + str(self.dummy_idx))
        if command == 'eq':
            self.line('D;JEQ')
        elif command == 'gt':
            self.line('D;JGT')
        elif command == 'lt':
            self.line('D;JLT')
        self.line('@SP')
        self.line('A=M-1')
        self.line('M=0')              # skipped if M == D
        self.line('(DUMMY' + str(self.dummy_idx) + ')')
        self.dummy_idx += 1

    def push_pop_helper(self, command, segment, index):
        """pull out segment translation
        note that we're assuming good syntax"""
        if segment in SEGMENT_DICT:
            asm_segment = '@' + SEGMENT_DICT[segment]
            self.line('@' + index)
            self.line('D=A')
            self.line(asm_segment)
            self.line('M=D+M')          # adjust LCL to LCL + index
            if command == 'C_PUSH':
                self.line('A=M')
                self.line('D=M')        # D is local + index value
                self.line('@SP')
                self.line('M=M+1')
                self.line('A=M-1')
                self.line('M=D')        # set stack to value
            else:  # C_POP
                self.line('@SP')
                self.line('AM=M-1')     # decrement stack position
                self.line('D=M')        # D is top of stack val
                self.line(asm_segment)
                self.line('A=M')
                self.line('M=D')        # set LCL+index to the new val
            self.line('@' + index)
            self.line('D=A')
            self.line(asm_segment)
            self.line('M=M-D')          # reset LCL to base
        else:
            if segment == 'temp':
                asm_segment = '@R' + str(int(index) + 5)
            elif segment == 'pointer':
                asm_segment = '@R' + str(int(index) + 3)
            else:
                asm_segment = '@' + str(int(index) + 16)
            if command == 'C_PUSH':
                self.line(asm_segment)
                self.line('D=M')
                self.line('@SP')
                self.line('M=M+1')
                self.line('A=M-1')
                self.line('M=D')
            else:   #C_POP
                self.line('@SP')
                self.line('AM=M-1')
                self.line('D=M')
                self.line(asm_segment)
                self.line('M=D')

    def write_push_pop(self, command, segment, index):
        """command - C_PUSH or C_POP
        segment - string
        index - int
        result: outputs asm code to file"""
        self.line(' '.join(['//', command, segment, index]))    # for debugging
        if segment == 'constant':       # can only be a C_PUSH
            self.line('@' + index)
            self.line('D=A')            # set D to constant val
            self.line('@SP')
            self.line('M=M+1')          # increment top stack
            self.line('A=M-1')
            self.line('M=D')            # set to top stack to constant val
        elif segment in ('local', 'argument', 'this', 'that', 'temp', 'pointer', 'static'):
            self.push_pop_helper(command, segment, index)
        else:
            print('not yet implemented')
