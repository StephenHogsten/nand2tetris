"""outputs tokens into xml"""
# TODO - it may be worth making a dictionary for keywords and token types to avoid typos

class CompilationEngine:
    """translate tokens into xml file"""
    def __init__(self, tokenizer, xml_file):
        """gets ready to create compiled file"""
        self.tokenizer = tokenizer
        self.xml_file = xml_file
        self.indent_level = 0

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


    def output_line(self, element, body='', include_open=True, include_close=True):
        """print a line of xml. by default it's an open and close tag with optional text in body
        element (required) - what to name this xml element
        body - what value to put inside the element
        include_open - default true, whether to include the open tag
        include_close - default true, whether ot include the close tag"""
        line = '  ' * self.indent_level
        if include_open:
            line += '<' + element + '>'
        else:
            self.indent_level -= 1
            line = '  ' * self.indent_level
        if body != '' and include_close:
            line += ' ' + body + ' '
        if include_close:
            line += '</' + element + '>'
        else:
            self.indent_level += 1
        self.xml_file.write(line)
        self.xml_file.write('\n')
        print(line)


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
        self.output_line('identifier', token)

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

        # type
        [token_type, token, error] = self.check_current_token(['KEYWORD', 'IDENTIFIER'], ['int', 'char', 'boolean'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # varName
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

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
            self.output_line(token_type.lower(), token)

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

        # void | type 
        [token_type, token, error] = self.check_current_token(['KEYWORD', 'IDENTIFIER'], ['void', 'int', 'char', 'boolean'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        #subroutineName
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

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
        self.output_line(token_type.lower(), token)

        # varName
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

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
            self.output_line(token_type.lower(), token)

            [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
            if error:
                return False
            self.output_line(token_type.lower(), token)

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

        # varName
        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        while True:
            [token_type, token, error] = self.check_current_token(['SYMBOL'], [','], silent=True)
            if error:
                break       # 0 is okay
            self.output_line(token_type.lower(), token)

            [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
            if error:
                return False
            self.output_line(token_type.lower(), token)

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
        self.output_line(token_type.lower(), token)

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
        
        # finish up
        self.output_line('ifStatement', include_open=False)
        return True

    def compile_while(self):
        """while statement is
        'while' '(' expression ')' '{' statements '}' """
        
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

        # finish up
        self.output_line('whileStatement', include_open=False)
        return True

        
    def compile_do(self):
        """do statement is 
        'do' subroutinecall ';' 
        """

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
        self.compile_expression(True)       # we don't care if it fails - it's optional

        # ;
        [token_type, token, error] = self.check_current_token(['SYMBOL'], [';'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # finish up
        self.output_line('returnStatement', include_open=False)
        return True
    
    def compile_subroutine_call(self, allow_zero=False):
        """subroutine call is 
        ((className | varName) '.')? subroutineName '(' expressionList ')' """

        [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        [token_type, token, error] = self.check_current_token(['SYMBOL'], ['.', '('])
        if error:
            return False
        self.output_line(token_type.lower(), token)
        if token == '.':
            # we included the optional part - get to the parenthesis
            [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
            if error:
                return False
            self.output_line(token_type.lower(), token)

            [token_type, token, error] = self.check_current_token(['SYMBOL'], ['('])
            if error:
                return False
            self.output_line(token_type.lower(), token)

        # expressionList
        if not self.compile_expression_list():
            return False

        # )
        [token_type, token, error] = self.check_current_token(['SYMBOL'], [')'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

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
        if token == 'INT_CONST':
            self.output_line('integerConstant', token)
        elif token == 'STRING_CONST':
            self.output_line('stringConstant', token)
        else:
            self.output_line(token_type.lower(), token)

        # do we need to keep going, or is it just a one token 
        if token in ('INT_CONST', 'STRING_CONST', 'KEYWORD'):
            pass        # nothing we have to do further
        elif token in ('~', '-'):       
            # -unaryOp- term
            if not self.compile_term():
                return False
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
            [token_type, token, error] = self.check_current_token(['SYMBOL'], ['(', '.', '['], silent=True)
            if error:
                pass    # just a varname - done
            else:
                self.output_line(token_type.lower(), token)
                if token == '(':
                    # -subroutineName (- expressionList )
                    if not self.compile_expression_list():
                        return False

                    [token_type, token, error] = self.check_current_token(['SYMBOL'], [')'])
                    if error:
                        return False
                    self.output_line(token_type.lower(), token)
                elif token == '.': 
                    # -class .- subroutine ( expression )
                    # I feel it's easier (though really it's worse) to just not use the subroutine call fn
                    # subroutine
                    [token_type, token, error] = self.check_current_token(['IDENTIFIER'])
                    if error:
                        return False
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

                elif token == '[':
                    # -varName [- expression ]
                    if not self.compile_expression():
                        return False

                    [token_type, token, error] = self.check_current_token(['SYMBOL'], [']'])
                    if error:
                        return False
                    self.output_line(token_type.lower(), token)

        # finish up
        self.output_line('term', include_open=False)
        return True

    def compile_expression_list(self):
        """expression list is 
        (expression (',' expression)* )?
        allows zero implicitly"""
        self.output_line('expressionList', include_close=False)

        # expression ... ?
        if self.compile_expression(allow_zero=True):

            # , expression *
            while True:
                [token_type, token, error] = self.check_current_token(['SYMBOL'], [','], silent=True)
                if error:
                    break
                self.output_line(token_type.lower(), token)

                if not self.compile_expression():
                    return False

        # finish up
        self.output_line('expressionList', include_open=False)
        return True

    
        