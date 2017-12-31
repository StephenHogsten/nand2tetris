"""create a new symbol table"""

# for the first iteration with the symbol table, we should add these attributes to the xml:
#   kind=[class|static|field|arg|var|subroutine]
#   usage=[used|declared]
#   index=[index number if it's static/field/arg/var]

class SymbolTableEntry:
    """data fields for each entry"""

    def __init__(self, entry_type, entry_kind, entry_index):
        self.type = entry_type
        self.kind = entry_kind
        self.index = entry_index

    def __repr__(self):
        return str({'type': self.type, 'kind': self.kind, 'index': self.index})

class SymbolTable:
    """generates symbol tables"""

    def __init__(self):
        self.class_hash = {}
        self.subroutine_hash = {}
        self.indexes = {
            'static': 0,
            'field': 0,
            'arg': 0,
            'var': 0
        }

    def __repr__(self):
        return str({
            'subroutine_hash': self.subroutine_hash,
            'class_hash': self.class_hash,
            'indexes': self.indexes
        })

    def start_subroutine(self):
        self.subroutine_hash = {}
        self.indexes['arg'] = 0
        self.indexes['var'] = 0

    def define(self, name, entry_type, kind):
        kind = kind.lower()
        if kind in self.indexes:
            self.indexes[kind] += 1
        else:
            self.indexes[kind] = 0
        new_entry = SymbolTableEntry(entry_type, kind, self.var_count(kind) - 1)
        if kind in ('arg', 'var'):
            self.subroutine_hash[name] = new_entry
        else:
            self.class_hash[name] = new_entry

    def var_count(self, kind):
        kind = kind.lower()
        if kind not in self.indexes:
            print('kind %s not found in indexes' % kind)
            print(self.indexes)
        return self.indexes[kind]

    def kind_of(self, var_name):
        """what kind of scope (e.g. arg, var)"""
        if var_name in self.subroutine_hash:
            return self.subroutine_hash[var_name].kind
        elif var_name in self.class_hash:
            return self.class_hash[var_name].kind
        else:
            return None

    def type_of(self, var_name):
        """what type of variable (e.g. string, int)"""
        if var_name in self.subroutine_hash:
            return self.subroutine_hash[var_name].type
        elif var_name in self.class_hash:
            return self.class_hash[var_name].type
        else:
            return None

    def index_of(self, var_name):
        if var_name in self.subroutine_hash:
            return self.subroutine_hash[var_name].index
        elif var_name in self.class_hash:
            return self.class_hash[var_name].index
        else:
            return None