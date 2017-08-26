import re

class JackTokenizer:
    """takes one input file and tokenizes the text"""

    def __init__(self, filename):
        """open file and set tokens to a giant array"""
        f = open(filename, 'r')
        lines = [line.split('//')[0].strip() for line in f.read().split('\n')]
        f.close()

        # build array of tokens and eliminate bracketed comments
        #   ! or " or & or b/w ( and ? (exclude @) or 
        valid_token = re.compile('\/\*|\*\/|\/\/|[!&(-/:-?\[\]{-~]|[0-9]+|[a-z]+|[0-9A-Za-z_][A-Za-z_]*|(?<=")[^"^\n]+"(?=")')
        dirty_tokens = ' '.join([line for line in lines if line != ''])  # dirty because it has comments
        dirty_tokens = valid_token.findall(dirty_tokens)
        print('-- dirty tokens --')
        print(dirty_tokens)
        in_comment = False
        self.tokens = []
        for token in dirty_tokens:
            if token in ('/*', '/**'):
                in_comment = True
                print('we are now in comment: ' + token)
            elif token == '*/':
                in_comment = False
                print('we are now NOT in comment: ' + token)
            elif not in_comment:
                self.tokens.append(token)
                print('we appended this comment: ' + token)

        self.current_token = None
        self.next_token_idx = 0
        print('-- clean tokens --')
        print(self.tokens)

    def has_more_tokens(self):
        """returns bool if there's a next line"""
        return self.next_token_idx < len(self.tokens)

    def advance(self):
        """advances - sets self.current_token
        assumes that has_more_tokens has been called"""
        self.current_token = self.tokens[self.next_token_idx]
        self.next_token_idx += 1

    def token_type(self):
        """returns type of current_token"""