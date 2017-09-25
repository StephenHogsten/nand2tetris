import os
from modules.jack_tokenizer import JackTokenizer
from modules.compilation_engine import CompilationEngine

def analyze(source):
  l = len(source)
  print('we\'re analyzing')
  if source.upper()[(l-5):] in ('.jack', '.JACK'):
    # one file
    print('this is one jack file')
    oneFile(source)
  else:
    # directory with many files
    print(source, ': this is a directory, not a file')
    for f in os.listdir(source):
      print(f)
      if f[len(f) - 5:].upper() == '.JACK':
        oneFile(os.path.join(source, f))

def oneFile(filename):
  file_base = filename[:len(filename) - 5]
  vm_filename = file_base + '.vm'
  tokenizer = JackTokenizer(filename)
  xml_filename = file_base + '.xml'
  xml_file = open(xml_filename, 'w')
  engine = CompilationEngine(tokenizer, xml_file)
  engine.compile_class()
  xml_file.close()