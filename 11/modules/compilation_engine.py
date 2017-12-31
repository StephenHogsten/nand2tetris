"""outputs tokens into xml"""

from modules.symbol_table import SymbolTable
from modules.vm_writer import VMWriter

ARITHMETIC_DICT = {
    '+': 'add',
    '-': 'sub',
    '=': 'eq',
    '>': 'gt',
    '<': 'lt',
    '&': 'and',
    '|': 'or'
}

UNARY_DICT = {
    '-': 'neg',
    '~': 'not'
}

# TODO - it may be worth making an enum or something for keywords and token types to avoid typos

class CompilationEngine:
    """translate tokens into xml file"""
    def __init__(self, tokenizer, xml_file, vm_file):
        """gets ready to create compiled file"""
        self.tokenizer = tokenizer
        self.xml_file = xml_file
        self.indent_level = 0
        self.symbol_table = None
        self.vm = VMWriter(vm_file)
        self.class_name = ''
        self.if_index = 0

    def check_current_token(self, expected_types, expected_tokens=None, silent=False, skip_advance=False):
        """try to get the current token and return it in [token_type, token, error], advancing if successful
        expected_types is an array of expected types
        exptected_tokens is an array of tokens we expect
        skip_advance prevents the advance at the end (should only be the last call)
        silent boots us out without throwing errors
        the last two parameters are for evaluating multiple instances of patterns"""
        error_start = 'error - expected ' + ' or '.join(expected_types)
        error_end = 'while writing ' + self.xml_file.name
        token_type = self.tokenizer.token_type()
        if token_type not in expected_types:
            error_message = ' '.join([error_start, 'and received type', token_type, error_end])
            if not silent:
                print(error_message)
            return [None, None, error_message]
        token = self.tokenizer.current_token
        if expected_tokens is None or len(expected_tokens) == 0:
            pass
        elif token_type in ['STRING_CONST', 'IDENTIFIER']:
            pass
        elif token_type == 'INT_CONST' and int(token) in range(32767):
            pass
        elif token in expected_tokens:
            pass
        else:
            error_message = ' '.join([error_start, 'and', ' or '.join(expected_tokens), 'and received token', token, error_end])
            if not silent:
                print(error_message)
            return [None, None, error_message]
        if not skip_advance:
            if not self.tokenizer.has_more_tokens():
                error_message = ' '.join([error_start, 'and file ended', error_end])
                if not silent:
                    print(error_message)
                return [None, None, error_message]
            self.tokenizer.advance()
        return [token_type, token, False]


    def output_line(self, element, body='', include_open=True, include_close=True, kind='', usage='', index=''):
        """print a line of xml. by default it's an open and close tag with optional text in body
        element (required) - what to name this xml element
        body - what value to put inside the element
        include_open - default true, whether to include the open tag
        include_close - default true, whether ot include the close tag"""
        line = '  ' * self.indent_level
        if include_open:
            str_usage = " usage=\"%s\"" % usage if usage else ''
            str_kind = " kind=\"%s\"" % kind if kind else ''
            str_index = " index=\"%d\"" % index if index or index == 0 else ''
            line += "<%s%s%s%s>" % (element, str_usage, str_kind, str_index)
        else:
            self.indent_level -= 1
            line = '  ' * self.indent_level
        if body != '' and include_close:
            translator = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}
            if body in translator:
                body = translator[body]
            line += ' ' + body + ' '
        if include_close:
            line += '</' + element + '>'
        else:
            self.indent_level += 1
        self.xml_file.write(line)
        self.xml_file.write('\n')


    def compile_class(self):
        """output for a class
        should be: 'class' className '{' classVarDec* subroutineDec* '}' 
        this and all other compile routines return whether it compiled successfully (true=success)"""
        self.tokenizer.advance()

        # class
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['class'])
        if error:
            return False
        self.output_line('class', include_close=False)
        self.output_line('keyword', 'class')
        
        # className
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.output_line('identifier', token, kind='class', usage='declared')
        self.symbol_table = SymbolTable()
        self.class_name = token

        # '{'
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['{'])
        if error:
            return False
        self.output_line('symbol', token)

        # classVarDec*
        # handling something 0 or more times is... a bit tricky
        while self.compile_class_var_dec(True):
            continue

        # subroutineDec*
        while self.compile_subroutine(True):
            continue

        # '}'
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['}'], skip_advance=True)
        if error:
            return False
        self.output_line('symbol', token)

        # finish up
        self.output_line('class', include_open=False)
        return True        


    def compile_class_var_dec(self, allow_zero=False):
        """output for a class variable declaration
        should be: ('static' | 'field') type varName (',' varName)* ';'"""
        
        # static | field
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['static', 'field'], silent=allow_zero)
        if error:
            return False
        self.output_line('classVarDec', include_close=False)
        self.output_line('keyword', token)
        kind = token.upper()

        # type
        [token_type, token, error] = self.check_current_token(['KEYWORD', 'IDENTIFIER'], ['int', 'char', 'boolean'])
        if error:
            return False
        if token_type == 'IDENTIFIER':
            self.output_line(token_type.lower(), token, kind='class', usage='used')
        else:
            self.output_line(token_type.lower(), token)
        var_type = token

        # varName
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.symbol_table.define(token, var_type, kind)
        self.output_line(token_type.lower(), token, kind=kind, usage='declared', index=self.symbol_table.var_count(kind) )

        # (',' varName)*)
        # ... tricky
        while True:
            [token_type, token, error] = self.check_current_token(['SYMBOL'], [','], silent=True)
            if error:
                break
            self.output_line(token_type.lower(), token)
            [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
            if error:
                return False
            self.symbol_table.define(token, var_type, kind)
            self.output_line(token_type.lower(), token, kind=kind, usage='declared', index=self.symbol_table.var_count(kind))

        # ';'
        [token_type, token, error] = self.check_current_token(['SYMBOL'], [';'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # finish up
        self.output_line('classVarDec', include_open=False)
        return True


    def compile_subroutine(self, allow_zero=False):
        """should be
        ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        where subroutineBody is '{' varDec* statements '}' """

        # constructor | function | method
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['constructor', 'function', 'method'], silent=allow_zero)
        if error:
            return False
        self.output_line('subroutineDec', include_close=False)
        self.output_line(token_type.lower(), token)

        # save off if it's a constructor
        if token == 'constructor':
            constructor = True
        elif token == 'method':
            constructor = False
            method = True
        else:
            constructor = False
            method = False

        # reset subroutine indexes
        self.symbol_table.start_subroutine()

        # void | type 
        [token_type, token, error] = self.check_current_token(['KEYWORD', 'IDENTIFIER'], ['void', 'int', 'char', 'boolean'])
        if error:
            return False
        if token_type == 'IDENTIFIER':
            self.output_line(token_type.lower(), token, kind='class', usage='used')
        else:
            self.output_line(token_type.lower(), token)

        #subroutineName
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.output_line(token_type.lower(), token, kind='subroutine', usage='declared' )

        vm_function = token

        # (
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['('])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # parameter list
        if not self.compile_parameter_list():
            return False

        # )
        [token_type, token, error] = self.check_current_token(['SYMBOL'], [')'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        self.output_line('subroutineBody', include_close=False)

        # {
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['{'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # varDec*
        while self.compile_var_dec(True):
            continue

        # VM - write the function declaration (I'm not positive anything above matter outside of the symbol table)
        self.vm.write_function("%s.%s" % (self.class_name, vm_function), self.symbol_table.var_count('var'))

        if constructor:
            # VM - if it's a constructor, use OS to allocate space, and store to 'this'
            self.vm.write_push('constant', self.symbol_table.var_count('field'))
            print('using constructor with %i fields' % self.symbol_table.var_count('field'))
            self.vm.write_call('Memory.alloc', 1)
            self.vm.write_pop('pointer', 0)
        elif method:
            # VM - if it's a method, set this to the first argument immediately
            self.vm.write_push('arg', 0)
            self.vm.write_pop('pointer', 0)

        # statements
        if not self.compile_statements():
            return False

        # }
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['}'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # finish up
        self.output_line('subroutineBody', include_open=False)
        self.output_line('subroutineDec', include_open=False)
        return True
    
    def compile_parameter_list(self):
        """should be
        ((type varName) (',' type varName)*)?
        allow zero is basically always allowed implicitly b/c the whole thing has a ?"""
        self.output_line('parameterList', include_close=False)

        # type
        [token_type, token, error] = self.check_current_token(['KEYWORD', 'IDENTIFIER'], ['int', 'char', 'boolean'], silent=True)
        if error:
            self.output_line('parameterList', include_open=False)
            return True     # it's okay if we fail - it just means we had zero
        if token_type == 'IDENTIFIER':
            self.output_line(token_type.lower(), token, kind='class', usage='used')
        else:
            self.output_line(token_type.lower(), token)
        var_type = token

        # varName
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.symbol_table.define(token, var_type, 'ARG')
        self.output_line(token_type.lower(), token, kind='ARG', usage='declared', index=self.symbol_table.var_count('ARG'))

        # (, type varName)*
        while True:
            # ,
            [token_type, token, error] = self.check_current_token(['SYMBOL'], [','], silent=True)
            if error:
                break       # we're done adding more if it fails
            self.output_line(token_type.lower(), token)

            # type
            [token_type, token, error] = self.check_current_token(['KEYWORD', 'IDENTIFIER'], ['int', 'char', 'boolean'])
            if error:
                return False
            if token_type == 'IDENTIFIER':
                self.output_line(token_type.lower(), token, kind='class', usage='used')
            else:
                self.output_line(token_type.lower(), token)
            var_type = token

            [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
            if error:
                return False
            self.symbol_table.define(token, var_type, 'ARG')
            self.output_line(token_type.lower(), token, kind='ARG', usage='declared', index=self.symbol_table.var_count('ARG'))

        # finish up
        self.output_line('parameterList', include_open=False)
        return True
        

    def compile_var_dec(self, allow_zero=False):
        """should be
        'var' type varName (',' varName)* ';' """
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['var'], silent=allow_zero)
        if error:
            return False
        self.output_line('varDec', include_close=False)
        self.output_line(token_type.lower(), token)

        # type
        [token_type, token, error] = self.check_current_token(['KEYWORD', 'IDENTIFIER'], ['int', 'char', 'boolean'])
        if error:
            return False
        self.output_line(token_type.lower(), token)
        var_type = token

        # varName
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.symbol_table.define(token, var_type, 'VAR')
        self.output_line(token_type.lower(), token, kind='ARG', usage='declared', index=self.symbol_table.var_count('VAR'))


        while True:
            [token_type, token, error] = self.check_current_token(['SYMBOL'], [','], silent=True)
            if error:
                break       # 0 is okay
            self.output_line(token_type.lower(), token)

            [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
            if error:
                return False
            self.symbol_table.define(token, var_type, 'VAR')
            self.output_line(token_type.lower(), token, kind='ARG', usage='declared', index=self.symbol_table.var_count('VAR'))

        # ;
        [token_type, token, error] = self.check_current_token(['SYMBOL'], [';'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # finish up
        self.output_line('varDec', include_open=False)
        return True
        
    def compile_statements(self):
        """should be
        statement* where statement is one of those below
        this implicitly allows 0"""
        self.output_line('statements', include_close=False)

        # choose which statement
        # all the statement functions assume we've already parse the keyword
        while True:
            [token_type, token, error] = self.check_current_token(['KEYWORD'], ['let', 'if', 'while', 'do', 'return'], silent=True, skip_advance=True)
            if error:
                break
            elif token == 'let':
                if not self.compile_let():
                    return False
            elif token == 'if':
                if not self.compile_if():
                    return False
            elif token == 'while':
                if not self.compile_while():
                    return False
            elif token == 'do':
                if not self.compile_do():
                    return False
            elif token == 'return':
                if not self.compile_return():
                    return False
        
        # finish up
        self.output_line('statements', include_open=False)
        return True

    def compile_let(self):
        """let statment is
        'let' varName ('[' expression ']')? '=' expression ';'
        """

        # let
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['let'])
        if error:
            return False
        self.output_line('letStatement', include_close=False)
        self.output_line(token_type.lower(), token)
        
        # varName
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        var_name = token
        var_kind = self.symbol_table.kind_of(token)
        var_index = self.symbol_table.index_of(token)
        self.output_line(token_type.lower(), token, kind=var_kind, usage='used', index=var_index)

        # [ expression ] ?
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['['], silent=True)
        if not error:
            self.output_line(token_type.lower(), token)

            # expression
            if not self.compile_expression():
                return False

            [token_type, token, error] = self.check_current_token(['SYMBOL'], [']'])
            if error:
                return False
            self.output_line(token_type.lower(), token)

            # for VM - we need to know later if we pushed the result from an expression as an array entry
            #   we can't set the address for 'that' because 'that' could be needed for the expressions on either side
            setting_array_entry = True
            
        else:
            setting_array_entry = False

        # =
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['='])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # expression
        if not self.compile_expression():
            return False

        # ;
        [token_type, token, error] = self.check_current_token(['SYMBOL'], [';'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # VM - set the variable
        print("--- let statement for %s  / %s ----" % (var_name, var_kind))
        if setting_array_entry:
            print(' NOTE: we ARE setting an array entry')
            self.vm.write_pop('temp', 0)        # save off the value while we set-up 'that'
            self.vm.write_push(var_kind, var_index)
            self.vm.write_arithmetic('add')     # add the variables value (array base) to the next value (should  be which index)
            self.vm.write_pop('pointer', 1)     # set this value as the address for 'that'
            self.vm.write_push('temp', 0)       # put the value back on top
            self.vm.write_pop('that', 0)        # put the value into the array's index
        else:
            # just set the variable the normal way
            self.vm.write_pop(var_kind, var_index)

        # finish up
        self.output_line('letStatement', include_open=False)
        return True
        

    def compile_if(self):
        """if statement is
        'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?"""
        # if
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['if'])
        if error:
            return False
        self.output_line("ifStatement", include_close=False)
        self.output_line(token_type.lower(), token)

        # (
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['('])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # expression
        if not self.compile_expression():
            return False

        # )
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ')')
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # VM - flip the conditional, then skip the initial statements if it's true
        self.vm.write_arithmetic('not')
        if_index = self.if_index
        self.if_index += 2
        self.vm.write_if("if_%i" % if_index)

        # {
        [token_type, token, error] = self.check_current_token(['SYMBOL'], '{')
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # statements
        if not self.compile_statements():
            return False

        # }
        [token_type, token, error] = self.check_current_token(['SYMBOL'], '}')
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # VM - make the label we'd skip to, skip over the next statements unless we got here without skipping
        self.vm.write_goto("if_%i" % (if_index + 1))
        self.vm.write_label("if_%i" % if_index)

        # else { statements } ?
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['else'], silent=True)
        if not error:
            self.output_line(token_type.lower(), token)

            # {
            [token_type, token, error] = self.check_current_token(['SYMBOL'], ['{'])
            if error:
                return False
            self.output_line(token_type.lower(), token)

            # statements 
            if not self.compile_statements():
                return False

            # }
            [token_type, token, error] = self.check_current_token(['SYMBOL'], ['}'])
            if error:
                return False
            self.output_line(token_type.lower(), token)
        
        # VM - label as the place to return to
        self.vm.write_label("if_%i" % (if_index + 1))

        # finish up
        self.output_line('ifStatement', include_open=False)
        return True

    
    def compile_while(self):
        """while statement is
        'while' '(' expression ')' '{' statements '}' """
        
        # VM - label the top of the loop to return to
        while_index = self.if_index
        self.if_index += 2
        self.vm.write_label("while_%i" % while_index)

        # while
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['while'])
        if error:
            return False
        self.output_line('whileStatement', include_close=False)
        self.output_line(token_type.lower(), token)

        # ( 
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['('])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # expression
        if not self.compile_expression():
            return False

        # )
        [token_type, token, error] = self.check_current_token(['SYMBOL'], [')'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # VM - skip the statements if the condition is not true
        self.vm.write_arithmetic('not')
        # print(self.if_index)
        # print(type(self.if_index))
        self.vm.write_if("while_%i" % (while_index + 1))

        # { 
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['{'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # statements
        if not self.compile_statements():
            return False

        # }
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['}'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # VM go back to the top to re-evaluate
        self.vm.write_goto('while_%i' % while_index)
        # VM label this as the place to skip to when the loop ends
        self.vm.write_label('while_%i' % (while_index + 1))

        # finish up
        self.output_line('whileStatement', include_open=False)
        return True

        
    def compile_do(self):
        """do statement is 
        'do' subroutinecall ';' """

        # do
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['do'])
        if error:
            return False
        self.output_line('doStatement', include_close=False)
        self.output_line(token_type.lower(), token)

        # subroutine call
        if not self.compile_subroutine_call():
            return False

        # ;
        [token_type, token, error] = self.check_current_token(['SYMBOL'], ';')
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # throwaway the returned value
        self.vm.write_pop('temp', 0)

        # finish
        self.output_line('doStatement', include_open=False)
        return True

    def compile_return(self):
        """return statement is 
        'return' expression? """
        self.output_line('returnStatement', include_close=False)

        # return
        [token_type, token, error] = self.check_current_token(['KEYWORD'], ['return'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # expression?
        # pass true to prevent 0 parts to the expression to cause a crash
        if not self.compile_expression(True):
            self.vm.write_push('const', 0)

        # ;
        [token_type, token, error] = self.check_current_token(['SYMBOL'], [';'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # finish up
        self.output_line('returnStatement', include_open=False)
        self.vm.write_return()
        return True
    
    def compile_subroutine_call(self, allow_zero=False, first_token=False, second_token=False):
        """subroutine call is 
        ((className | varName) '.')? subroutineName '(' expressionList ')' 
        passing first_token and second_token means we've already retrieved them and we're just calling this to handle the subroutine call"""

        if not first_token:
            [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
            if error:
                return False
            first_token = [token_type.lower(), token]

        if not second_token:
            [token_type, token, error] = self.check_current_token(['SYMBOL'], ['.', '('])
            if error:
                return False
            second_token = [token_type.lower(), token]
        else:
            [token_type, token] = second_token

        if token == '.':
            # we have XXX.
            first_token += [True, True, 'class', 'used']
            self.output_line(*first_token)
            self.output_line(*second_token)
            # we included the optional part - get to the parenthesis
            [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
            if error:
                return False
            self.output_line(token_type.lower(), token, kind='subroutine', usage='used')
            
            #VM - check whether it's a method call by whether the function is contained in a class or an object
            object_name = first_token[1]
            object_type = self.symbol_table.type_of(object_name)
            kind = self.symbol_table.kind_of(object_name)
            print('we\'re looking for %s %s %s' % (object_name, object_type, kind))
            if kind is None:
                # we're calling a class function - don't need to push 'this'
                n_args = [0]
                function_name = "%s.%s" % (object_name, token)
                print(' and we didn\'t find it')
            else:
                print(' and we DID find it')
                idx = self.symbol_table.index_of(object_name)
                if kind == 'static':
                    self.vm.write_push('static', idx)
                elif kind == 'field':
                    self.vm.write_push('this', idx)
                elif kind == 'arg':
                    self.vm.write_push('arg', idx)
                elif kind == 'var':
                    self.vm.write_push('local', idx)
                function_name = "%s.%s" % (object_type, token)      # either way we use the class of the object
                n_args = [1]

            [token_type, token, error] = self.check_current_token(['SYMBOL'], ['('])
            if error:
                return False
            self.output_line(token_type.lower(), token)
        else:
            # we have functionName(
            # no xxx. means that it's a method on the current object (instance method)
            # the function will be named with the current class
            first_token += [True, True, 'subroutine', 'used']
            self.output_line(*first_token)
            self.output_line(*second_token)
            # VM - push this onto the stack
            self.vm.write_push('pointer', 0)
            # set the function name to just the first token
            function_name = "%s.%s" % (self.class_name, first_token[1])
            n_args = [1]

        # expressionList
        if not self.compile_expression_list(n_args):
            return False

        # )
        [token_type, token, error] = self.check_current_token(['SYMBOL'], [')'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # VM - actually call the function now that the arguments are on the stack
        self.vm.write_call(function_name, n_args[0])

        # finish up
        return True
        

    def compile_expression(self, allow_zero=False):
        """expression is 
        term (op term)*
        where op is one of: + - * / & | < > = """
        # term 
        if not self.compile_term(allow_zero=allow_zero, prefix=lambda: self.output_line('expression', include_close=False)):
            # we're using a 'prefix' to add the expression block only when it should be
            return False
        
        # op term *
        while True:
            [token_type, token, error] = self.check_current_token(['SYMBOL'], ['+', '-', '*', '/', '&', '|', '<', '>', '='], silent=True)
            if error:
                break       # we've reached the end of the list
            self.output_line(token_type.lower(), token)

            if not self.compile_term():
                return False
            else:
                # perform operation if we found a term
                if token in ARITHMETIC_DICT:
                    self.vm.write_arithmetic(ARITHMETIC_DICT[token])
                elif token == '*':
                    self.vm.write_call('Math.multiply', 2)
                elif token == '/':
                    self.vm.write_call('Math.divide', 2)
                else:
                    print("Invalid operation: %s" % token)

        # finish up
        self.output_line('expression', include_open=False)
        return True

    def compile_term(self, allow_zero=False, prefix=None):
        """prefix is to specify a function to execute upon success
        term is
        integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        where 
            unaryOp is one of: - ~ 
            keywordConstant is one of: true, false, null, this"""

        [token_type, token, error] = self.check_current_token(['INT_CONST', 'STRING_CONST', 'KEYWORD', 'IDENTIFIER', 'SYMBOL'], ['(', '~', '-', 'true', 'false', 'null', 'this'], silent=allow_zero)
        if error:
            return False
        
        # print out the prefix function if necessary
        if prefix is not None:
            prefix()
        
        # open the term block
        self.output_line('term', include_close=False)

        # constants don't simply translate with .lower()
        if token_type == 'INT_CONST':
            self.output_line('integerConstant', token)
            self.vm.write_push('const', int(token))
        elif token_type == 'STRING_CONST':
            token_string = token[1: len(token) - 1]     # don't include the "
            self.output_line('stringConstant', token_string)
            self.vm.write_push('const', len(token_string))
            self.vm.write_call("String.new", 1)
            for i in token_string:
                self.vm.write_push('const', ord(i))
                self.vm.write_call('String.appendChar', 2)  # each should push the resulting object back on top of stack
            # when we leave the loop, the string object shold be complete and left on top
        elif token_type == 'KEYWORD':
            if token == 'true':
                self.vm.write_push('const', 1)     # true - 111...
                self.vm.write_arithmetic('neg')
            elif token == 'this':
                self.vm.write_push('pointer', 0)
            else:
                self.vm.write_push('const', 0)  # null or false - 000...
        elif token_type == 'IDENTIFIER':
            var_kind = self.symbol_table.kind_of(token)
            var_index = self.symbol_table.index_of(token)
            self.output_line(token_type.lower(), token, kind=var_kind, usage='used', index=var_index)
        else:
            self.output_line(token_type.lower(), token)

        # do we need to keep going, or is it just a one token 
        if token_type in ('INT_CONST', 'STRING_CONST', 'KEYWORD'):
            pass        # nothing we have to do further
        elif token in ('~', '-'):       
            # -unaryOp- term
            if not self.compile_term():
                return False
            self.vm.write_arithmetic(UNARY_DICT[token])
        elif token == '(':
            # -(- expression )
            if not self.compile_expression():
                return False

            [token_type, token, error] = self.check_current_token(['SYMBOL'], [')'])
            if error:
                return False
            self.output_line(token_type.lower(), token)
        else:
            # at this point it's either just varName, varName [ expression ], or subroutine
            first_token = [token_type.lower(), token]        # in case we're going to compile_subroutine_call

            [token_type, token, error] = self.check_current_token(['SYMBOL'], ['(', '.', '['], silent=True)
            if error:
                # just a varname, just push to stack. var_kind and var_index **should've** been set above
                self.vm.write_push(var_kind, var_index)
            else:
                self.output_line(token_type.lower(), token)
                if token == '[':
                    # -varName [- expression ]
                    if not self.compile_expression():
                        return False

                    [token_type, token, error] = self.check_current_token(['SYMBOL'], [']'])
                    if error:
                        return False
                    self.output_line(token_type.lower(), token)
                    # VM - add this to the variable to set the address for 'that' then retrieve the value there
                    self.vm.write_push(var_kind, var_index)
                    self.vm.write_arithmetic('add')
                    self.vm.write_pop('pointer', 1)
                    self.vm.write_push('that', 0)

                else:
                    # prepare to call subroutine handler
                    second_token = [token_type.lower(), token]
                    self.compile_subroutine_call(first_token=first_token, second_token=second_token)

        # TODO - I think I need to handle when the first token is 'this'

        # finish up
        self.output_line('term', include_open=False)
        return True

    def compile_expression_list(self, n_args):
        """expression list is 
        (expression (',' expression)* )?
        allows zero implicitly
        n_args is an array where the first index is a count of arguments so it can be passed back"""
        self.output_line('expressionList', include_close=False)

        # expression ... ?
        if self.compile_expression(allow_zero=True):
            n_args[0] += 1

            # , expression *
            while True:
                [token_type, token, error] = self.check_current_token(['SYMBOL'], [','], silent=True)
                if error:
                    break
                self.output_line(token_type.lower(), token)

                if not self.compile_expression():
                    return False

                # we just added another argument
                n_args[0] += 1

        # finish up
        self.output_line('expressionList', include_open=False)
        return True

    
        