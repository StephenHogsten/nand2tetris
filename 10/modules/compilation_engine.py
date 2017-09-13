"""outputs tokens into xml"""


class CompilationEngine:
    """translate tokens into xml file"""
    def __init__(self, tokenizer, xml_file):
        """gets ready to create compiled file"""
        self.tokenizer = tokenizer
        self.xml_file = xml_file
        self.indent_level = 0

    def try_next(self, expected_types, expected_tokens=None, skip_advance=False, silent=False):
        """try to get the next token and return it in [token_type, token, error]
        expected_types is an array of expected types
        exptected_tokens is an array of tokens we expect
        skip_advance uses the current token instead of advancing first
        silent boots us out without throwing errors
        the last two parameters are for evaluating multiple instances of patterns"""
        error_start = 'error - expected ' + ' or '.join(expected_types)
        error_end = 'while writing ' + self.xml_file.name
        if not skip_advance:
            if not self.tokenizer.has_more_tokens():
                error_message = ' '.join([error_start, 'and file ended', error_end])
                if not silent:
                    print(error_message)
                return [None, None, error_message]
            self.tokenizer.advance()
        token_type = self.tokenizer.token_type()
        if token_type not in expected_types:
            error_message = ' '.join([error_start, 'and received type', token_type, error_end])
            if not silent:
                print(error_message)
            return [None, None, error_message]
        token = self.tokenizer.current_token
        if expected_tokens is None or token_type in ['INT_CONST', 'STRING_CONST', 'IDENTIFIER'] or token in expected_tokens:
            return [token_type, token, False]
        error_message = ' '.join([error_start, 'and received token', token, error_end])
        if not silent:
            print(error_message)
        return [None, None, error_message]


    def output_line(self, element, body='', include_open=True, include_close=True):
        """print a line of xml. by default it's an open and close tag with optional text in body
        element (required) - what to name this xml element
        body - what value to put inside the element
        include_open - default true, whether to include the open tag
        include_close - default true, whether ot include the close tag"""
        line = '  ' * self.indent_level
        if include_open:
            line += '<' + element + '>'
        if body != '' and include_close:
            line += ' ' + body + ' '
        if include_close:
            line += '</' + element + '>'
        self.xml_file.write(line)
        self.xml_file.write('\n')
        print(line)


    def compile_class(self):
        """output for a class
        should be: 'class' className '{' classVarDec* subroutineDec* '}' 
        this and all other compile routines return whether it compiled successfully (true=success)"""
        # class
        [token_type, token, error] = self.try_next(['KEYWORD'], ['class'])
        if error:
            return False
        self.output_line('class', include_close=False)
        self.output_line('keyword', 'class')
        self.indent_level += 1
        
        # className
        [token_type, token, error] = self.try_next(['IDENTIFIER'])
        if error:
            return False
        self.output_line('identifier', token)

        # '{'
        [token_type, token, error] = self.try_next(['SYMBOL'], ['{'])
        if error:
            return False
        self.output_line('symbol', token)

        # classVarDec*
        # handling something 0 or more times is... tricky
        while self.compile_class_var_dec(allow_zero=True):
            continue

        # subroutineDec*
        skip_advance = True
        while self.compile_subroutine(skip_advance, True):
            skip_advance = False    # this means we'll skip the first and advance after that

        # '}'
        [token_type, token, error] = self.try_next(['SYMBOL'], ['}'])
        if error:
            return False
        self.output_line('symbol', token)

        # finish up
        self.output_line('class', include_open=False)
        return True        


    def compile_class_var_dec(self, skip_first_advance=False, allow_zero=False):
        """output for a class variable declaration
        should be: ('static' | 'field') type varName (',' varName)* ';'"""
        # static | field
        [token_type, token, error] = self.try_next(['KEYWORD'], ['static', 'field'], skip_first_advance, silent=allow_zero)
        if error:
            return False
        self.output_line('keyword', token)

        # type
        [token_type, token, error] = self.try_next(['KEYWORD', 'IDENTIFIER'], ['int', 'char', 'boolean',])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # varName
        [token_type, token, error] = self.try_next(['IDENTIFIER'])
        if error:
            return False
        self.output_line(token_type.lower(), token)

        # (',' varName)*)
        # ... tricky
        while True:
            [token_type, token, error] = self.try_next(['SYMBOL'], [','], silent=True)
            if error:
                break
            self.output_line(token_type.lower(), token)
            [token_type, token, error] = self.try_next(['IDENTIFIER'])
            if error:
                return False
            self.output_line(token_type.lower(), token)

        # ';'
        [token_type, token, error] = self.try_next(['SYMBOL'], [';'], True)
        if error:
            return False
        self.output_line(token_type.lower(), token)


    def compile_subroutine(self, skip_first_advance=False, allow_zero=False):
        self.output_line('placeholder', 'subroutine')
        return False

        