import os
from modules.jack_tokenizer import JackTokenizer

def analyze(source):
  l = len(source)
  print('we\'re analyzing')
  if source.upper()[(l-5):] in ('.jack', '.JACK'):
    # one file
    print('this is one jack file')
    oneFile(source)
  else:
    # directory with many files
    print('this is a directory, not a file')


def oneFile(filename):
  vm_filename = filename[:len(filename) - 5] + '.vm'
  tokenizer = JackTokenizer(filename)