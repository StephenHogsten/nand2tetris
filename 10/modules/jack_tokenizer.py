import re

class JackTokenizer:
    """takes one input file and tokenizes the text"""

    def __init__(self, filename):
        """open file and set tokens to a giant array"""
        f = open(filename, 'r')
        lines = [line.split('//')[0].strip() for line in f.read().split('\n')]
        f.close()

        # build array of tokens and eliminate bracketed comments
        valid_token = re.compile('\/\*|\*\/|\/\/|[!&(-/:-?\[\]{-~]|[0-9]+|[0-9A-Za-z_][A-Za-z_]*|[a-z]+|"[^"^\n]+"')
        dirty_tokens = ' '.join([line for line in lines if line != ''])  # dirty because it has comments
        dirty_tokens = valid_token.findall(dirty_tokens)
        in_comment = False
        self.tokens = []
        for token in dirty_tokens:
            if token in ('/*', '/**'):
                in_comment = True
            elif token == '*/':
                in_comment = False
            elif not in_comment:
                self.tokens.append(token)

        print(self.tokens)
        self.current_token = None
        self.next_token_idx = 0

    def has_more_tokens(self):
        """returns bool if there's a next line"""
        return self.next_token_idx < len(self.tokens)

    def advance(self):
        """advances - sets self.current_token
        assumes that has_more_tokens has been called"""
        self.current_token = self.tokens[self.next_token_idx]
        self.next_token_idx += 1

    def token_type(self, token=None):
        """returns type of current_token"""
        if token is None:
            token = self.current_token
        if token in ('class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'):
            return 'KEYWORD'
        elif len(token) == 1 and token in '{}()[].,;+-*/^|<>=-':
            return 'SYMBOL'
        elif re.fullmatch('[0-9]{1,5}', token) and int(token) < 32768:
            return 'INT_CONST'
        elif re.fullmatch('[0-9A-Za-z_][A-Za-z_]*', token):
            return 'IDENTIFIER'
        elif re.fullmatch('"[^"^\n]+"', token):
            return 'STRING_CONST'
        else:
            return 'invalid string'

    # For all these routines I'm fine with just assuming it's good since we'll always call token_type first
    def key_word(self):
        """return which keyword current token represents"""
        return self.current_token.upper()
    
    def symbol(self):
        """return the symbol"""
        return self.current_token

    def identifier(self):
        """return the identifier"""
        return self.current_token

    def int_val(self):
        """return the integer value"""
        return int(self.current_token)

    def string_val(self):
        """return the string value"""
        return self.current_token