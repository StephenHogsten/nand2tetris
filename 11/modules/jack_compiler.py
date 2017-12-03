"""top level module that calls others to create vm files"""
import os
from modules.jack_tokenizer import JackTokenizer
from modules.compilation_engine import CompilationEngine


def compile_jack(source):
    """check the source type and either generate one vm file or loop through directory"""
    l = len(source)
    print('we\'re analyzing')
    if source.upper()[(l-5):] in ('.jack', '.JACK'):
        # one file
        print('this is one jack file')
        one_file(source)
    else:
        # directory with many files
        print(source, ': this is a directory, not a file')
        for f in os.listdir(source):
            print(f)
            if f[len(f) - 5:].upper() == '.JACK':
                one_file(os.path.join(source, f))

def one_file(filename):
    """generate vm file for a single .jack file"""
    file_base = filename[:len(filename) - 5]
    # vm_filename = file_base + '.vm'
    tokenizer = JackTokenizer(filename)
    xml_filename = file_base + '.xml'
    vm_filename = file_base + '.vm'
    xml_file = open(xml_filename, 'w')
    vm_file = open(vm_filename, 'w')
    engine = CompilationEngine(tokenizer, xml_file, vm_file)
    engine.compile_class()
    xml_file.close()