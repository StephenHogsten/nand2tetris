"""writes vm commands to a given vm file"""

SEGMENT_DICT = {
    'const': 'constant',
    'arg': 'argument',
    'field': 'this',
    'var': 'local'
}

class VMWriter:
    """write vm commands to file"""
    def __init__(self, vm_file):
        self.file = vm_file
    
    def write(self, content):
        """helper to write a line"""
        self.file.write(content)

    def newline(self):
        """helper to write a new line character"""
        self.write('\n')

    def write_push(self, segment, index):
        """writes a vm push command
        segment is const | arg | local | static | this | that | pointer | temp"""
        if segment in SEGMENT_DICT:
            segment = SEGMENT_DICT[segment]
        else: 
            self.write("push %s %i" % (segment, index))
        self.newline()

    def write_pop(self, segment, index):
        """writes a vm pop command
        segment is const | arg | local | static | this | that | pointer | temp"""
        if segment in SEGMENT_DICT:
            segment = SEGMENT_DICT[segment]
        self.write("pop %s %i" % (segment, index))
        self.newline()

    def write_arithmetic(self, command):
        """writes an arithmetic command 
        (performed on the first or first and second elements on the stack)
        add | sub | neg | eq | gt | lt | and | or | not """
        self.write(command.lower())
        self.newline()

    def write_label(self, label):
        """writes a label command"""
        self.write("label %s" % label)
        self.newline()

    def write_goto(self, label):
        """writes a goto command"""
        self.write("goto %s" % label)
        self.newline()

    def write_if(self, label):
        """writes an if command (goto if top of stack is true)"""
        self.write("if-goto %s" % label)
        self.newline()

    def write_call(self, name, n_args):
        """writes a call command (call subroutine)"""
        self.write("call %s %i" % (name, n_args))
        self.newline()

    def write_function(self, name, n_locals):
        """writes a function command"""
        self.write("function %s %i" % (name, n_locals))
        self.newline()

    def write_return(self):
        """writes a return command"""
        self.write('return')
        self.newline()