"""make vm files from jack files"""
import sys

from modules.jack_analyzer import analyze

def process_input():
    """decide the mode based on input
    should always receive one parameter, may be a directory or a jack filename"""
    if len(sys.argv) < 2:
        print('must give one input: a .jack file or a directory containing them')
    else:
        analyze(sys.argv[1])

if __name__ == '__main__':
    process_input()
else:
    print('Must be called from command line')