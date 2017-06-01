"""creates a symbol table with memory locations or values for symbols
"""


class SymbolTable:
    def __init__(self):
        """initialize symbol table"""
        self.table = {}

    def add_entry(self, symbol, address):
        self.table[symbol] = address

    def contains(self, symbol):
        return symbol in self.table

    def get_address(self, symbol):
        return self.table[symbol]
