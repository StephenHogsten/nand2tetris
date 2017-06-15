"""calls makes asm files based on vm files"""
# pylint: disable=E0402
# pylint: disable=C0103

import sys
import os
from modules.asm_writer import Writer
from modules.vm_parser import Parser


def one_vm_file(filename, asm):
    """parses one vm file into a given asm file"""
    vm = Parser(filename)
    while vm.has_more_commands():
        vm.advance(False)
        command_type = vm.command_type()
        if command_type == 'C_ARITHMETIC':
            asm.write_arithmetic(vm.arg1())
        elif command_type in ('C_PUSH', 'C_POP'):
            asm.write_push_pop(command_type, vm.arg1(), vm.arg2())
        else:
            print('command', command_type, 'not implemented')


def vm_directory(directory):
    """traverses a directory to parse vm files"""
    asm = Writer()
    if directory:
        last_dir = os.path.split(directory)[1]
        asm.set_filename(directory + '/' + last_dir)
        prefix = directory + '/'
    else:
        directory = None
        prefix = ''
        asm.set_filename(os.path.split(os.getcwd())[1])
    for f in os.listdir(directory):
        if f[len(f) - 3:] == '.vm':
            one_vm_file(prefix + f, asm)
    asm.close()
    print('done')


def process_input():
    """decide the mode based on input"""
    if len(sys.argv) < 2:
        vm_directory(None)
        return
    else:
        user_input = sys.argv[1]
    base_idx = len(user_input) - 3
    if user_input[base_idx:] in ('.vm', '.VM'):
        filebase = user_input[:base_idx]
        asm_writer = Writer()
        asm_writer.set_filename(filebase)
        one_vm_file(user_input, asm_writer)
        asm_writer.close()
        print('done')
    else:
        vm_directory(user_input)


if __name__ == '__main__':
    process_input()
else:
    print("can only be called from commmand line")
