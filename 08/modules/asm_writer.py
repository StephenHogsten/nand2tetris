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
        self.location = 0
        self.function_arr = ['no_function']
        self.function_dict = {'no_function': 0}
        self.current_function = self.function_arr[0]

    def name(self):
        """print filename"""
        return self.file.name

    def line(self, command, skip_increment=False):
        """shortcut for appending a new line of text"""
        self.file.write(command)
        # self.file.write(str(self.location) + ' ' + command)
        self.file.write('\n')
        if not skip_increment:
            self.location += 1

    def set_filename(self, filename):
        """opens file with specified name"""
        self.file = open(filename + '.asm', 'w')

    def close(self):
        """close output file"""
        self.file.close()

    def write_init(self):
        """run 'bootstrap code'"""
        # set SP to 256
        self.line('@256')
        self.line('D=A')
        self.line('@SP')
        self.line('M=D')

    def write_arithmetic(self, command):
        """takes VM code and outputs asm code to file"""
        self.line('// ' + command, True)      # for easier debugging
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
        self.line('@' + str(self.location + 5))
        if command == 'eq':
            self.line('D;JEQ')
        elif command == 'gt':
            self.line('D;JGT')
        elif command == 'lt':
            self.line('D;JLT')
        self.line('@SP')
        self.line('A=M-1')
        self.line('M=0')              # skipped if M == D

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
                asm_segment = '@' + str(int(index) + 5)
            elif segment == 'pointer':
                asm_segment = '@' + str(int(index) + 3)
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
        self.line(' '.join(['//', command, segment, index]), True)    # for debugging
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
            print('invalid command')

    def scope_label(self, label):
        """extract for forming function scoped label"""
        return self.current_function + '$' + label

    def write_label(self, label):
        """write out label command"""
        self.line(' '.join(['//', 'Label', label]), True)
        label = self.scope_label(label)
        self.line('(' + label + ')', True)

    def write_goto(self, label):
        """goto label"""
        self.line(' '.join(['//', 'goto', label]), True)
        label = self.scope_label(label)
        self.line('@' + label)
        self.line('0;JMP')

    def write_if(self, label):
        """goto label if pop of stack is not zero"""
        self.line(' '.join(['//', 'goto-if', label]), True)
        label = self.scope_label(label)
        self.line('@SP')
        self.line('AM=M-1')
        self.line('D=M')
        self.line('@' + label)
        self.line('D;JNE')

    def write_function(self, function_name, local_cnt):
        """declare a function"""
        self.line(' '.join(['//', 'function', function_name, local_cnt]), True)
        self.line('(' + function_name + ')', True)        # does this need to be prefixed?
        self.function_arr.append(function_name)       # save our function to array "stack"
        self.function_dict[function_name] = local_cnt   # save how many locals (for return statements)
        self.current_function = function_name
        for i in range(int(local_cnt)):
            # pushing onto the stack for each local variable?
            self.write_push_pop('C_PUSH', 'constant', '0')
        # I think this is all we do?

    def return_set_bases(self, base_name):
        """pop stack to reset a base pointer value"""
        self.line('@FRAME')
        self.line('AM=M-1')
        self.line('D=M')
        self.line('@' + base_name)
        self.line('M=D')

    def write_return(self):
        """set-up the entire frame back to the caller"""
        # write line for debugging
        self.line('// return', True)
        # reset the current function (for scoping labels)
        ending_function = self.function_arr.pop()
        self.current_function = self.function_arr[len(self.function_arr) - 1]
        
        # book pseudo - code to asm translation
        # frame = lcl: lcl is the end of the new frame, store this somewhere
        self.line('@LCL')
        self.line('D=M')
        self.line('@FRAME')
        self.line('M=D')
        # ret = *frame - 5: at end of frame is ret, local, arg, this, that, save off ret
        self.line('@5')
        self.line('D=A')
        self.line('@FRAME')     # temporary variable containing end of new frame
        self.line('A=M-D')      # value of end of new frame location - 5 (where ret is)
        self.line('D=M')        # store the return address to D
        self.line('@RET')       
        self.line('M=D')        # save the return address to the temp variable
        # *arg = pop(): the fn return value is current at top of stack, current arg location will become top of new stack
        self.write_push_pop('C_POP', 'argument', '0')
        # sp = arg + 1: set the top of the stack to current arg
        self.line('@ARG')
        self.line('D=M+1')
        self.line('@SP')
        self.line('M=D')
        #THAT = *(frame - 1): restore old that using the frame temp variable location
        self.return_set_bases('THAT')
        #THIS = *(frame - 2): restore old this using the frame temp variable location
        self.return_set_bases('THIS')
        #ARG = *(frame - 3): restore old arg using the frame temp variable location
        self.return_set_bases('ARG')
        #LCL = *(frame - 4): restore old lcl using the frame temp variable location
        self.return_set_bases('LCL')
        #goto RET: everything is set-up like it was before the call, resume execution
        self.line('@RET')
        self.line('A=M')
        self.line('0;JMP')

    def call_push_bases(self, base_name):
        self.line('@' + base_name)
        self.line('D=M')
        self.line('@SP')
        self.line('M=M+1')
        self.line('A=M-1')
        self.line('M=D')

    def write_call(self, function_name, arg_cnt):
        """call a function - push the current frame to the stack and goto the instructions"""
        self.line(' '.join(['//', function_name, arg_cnt]), True)
        # push return address label
        return_label = '$call_' + function_name + '_' + str(self.location)
        self.line('@' + return_label)
        self.line('D=A')
        self.line('@SP')
        self.line('M=M+1')
        self.line('A=M-1')
        self.line('M=D')
        # push local
        self.call_push_bases('LCL')
        # push arg
        self.call_push_bases('ARG')
        # push this
        self.call_push_bases('THIS')
        # push that
        self.call_push_bases('THAT')
        # arg = sp-n-5: args are what was pushed before frame stuff
        #   A is already set to SP
        self.line('D=A')
        self.line('@' + str(4 + int(arg_cnt)))
        self.line('D=D-A')
        self.line('@ARG')
        self.line('M=D')
        # LCL = SP
        self.line('@SP')
        self.line('D=M')
        self.line('@LCL')
        self.line('M=D')
        #goto f
        self.line('@' + function_name)
        self.line('0;JMP')
        self.line('(' + return_label + ')', True)