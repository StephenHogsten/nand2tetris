"""Code Module for assembler. Translates mnemonics to binary strings
"""


def dest(mnemonic):
    """translates destination mnemonic to binary"""
    res = ['0', '0', '0']
    if 'A' in mnemonic:
        res[0] = '1'
    if 'D' in mnemonic:
        res[1] = '1'
    if 'M' in mnemonic:
        res[2] = '1'
    return ''.join(res)


def comp_w_a(mnem):
    """first comp split: mnemonics with A"""
    if mnem == 'A':
        ans = '0110000'
    elif mnem == '!A':
        ans = '0110001'
    elif mnem == '-A':
        ans = '0110011'
    elif mnem == 'A+1':
        ans = '0110111'
    elif mnem == 'A-1':
        ans = '0110010'
    elif mnem == 'D+A':
        ans = '0000010'
    elif mnem == 'D-A':
        ans = '0010011'
    elif mnem == 'A-D':
        ans = '0000111'
    elif mnem == 'D&A':
        ans = '0000000'
    else:
        ans = '0010101'
    return ans


def comp_no_m(mnem):
    """2nd comp split: mnemoics w/o M"""
    if mnem == '0':
        ans = '0101010'
    elif mnem == '1':
        ans = '0111111'
    elif mnem == '-1':
        ans = '0111010'
    elif mnem == 'D':
        ans = '0001100'
    elif mnem == '!D':
        ans = '0001101'
    elif mnem == '-D':
        ans = '0001111'
    elif mnem == 'D+1':
        ans = '0011111'
    elif mnem == 'D-1':
        ans = '0001110'
    else:
        # could be a ;JMP or something like that
        ans = '0101010'
    return ans


def comp_w_m(mnem):
    """last comp split: mnemonics w/ m"""
    if mnem == 'M':
        ans = '1110000'
    elif mnem == '!M':
        ans = '1110001'
    elif mnem == '-M':
        ans = '1110011'
    elif mnem == 'M+1':
        ans = '1110111'
    elif mnem == 'M-1':
        ans = '1110010'
    elif mnem == 'D+M':
        ans = '1000010'
    elif mnem == 'D-M':
        ans = '1010011'
    elif mnem == 'M-D':
        ans = '1000111'
    elif mnem == 'D&M':
        ans = '1000000'
    elif mnem == 'D|M':
        ans = '1010101'
    else:
        ans = 'error'
    return ans


def comp(mnem):
    """parse calculation mnemonic"""
    if 'A' in mnem:
        ans = comp_w_a(mnem)
    elif 'M' not in mnem:
        ans = comp_no_m(mnem)
    else:
        ans = comp_w_m(mnem)
    return ans


def jump(mnem):
    """parse jump mnemonic"""
    if mnem == '':
        return '000'
    if mnem == 'JNE':
        return '101'
    if mnem == 'JMP':
        return '111'
    b = ['0'] * 3
    if 'E' in mnem:
        b[1] = '1'
    if 'G' in mnem:
        b[2] = '1'
    if 'L' in mnem:
        b[0] = '1'
    return ''.join(b)
