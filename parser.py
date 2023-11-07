'''
Reads the input code line-by-line and provides input to different components
'''

import os, sys
import re

class Parser:
    def __init__(self, input_file):
        self.code = []
        with open(input_file, 'r') as f: self.code = f.readlines()
        self.mem_code, self.instrs = self.parse_lines(self.code)


    def get_mem_initialization(self):
        return self.mem_code


    def get_instructions(self):
        return self.instrs


    def parse_lines(self, code):
        mem_code = []
        instrs = []
        label_instrline = {}
        for line in code:
            line = line.strip()
            if len(line) == 0: continue         # empty line
            if line.startswith('%'): continue   # comment

            m = re.search(r'^(\d+),\s*(\d+)$', line)
            if m:                               # memory content
                addr = m.group(1)
                val = m.group(2)
                mem_code.append((addr, val))
                continue

            m = re.search(r'(\w+):', line)
            if m:                               # label
                label = m.group(1).strip()
                instrline = len(instrs)
                label_instrline[label] = 4 * instrline
                continue

            m = re.search(r'^\D+\s+.+,', line)
            if m:                               # instruction
                instrs.append(line)
                continue

            assert False, f'Unexpected line in the input file: {line}'

        # pre-process: replace labels with instruction lines
        for i, instr in enumerate(instrs):
            m = re.search(r'bne .*,.*,(.*)$', instr)
            if not m: continue
            label = m.group(1).strip()
            assert label in label_instrline.keys(), f'label:{label}, label_instrline:{label_instrline}'
            instrs[i] = instr.replace(label, str(label_instrline[label]))

        return mem_code, instrs


if __name__ == '__main__':
    if len(sys.argv[1:]) != 1:
        print(f'Usage: {argv[0]} path/to/input/file')
        exit(1)

    filename = sys.argv[1]
    assert os.path.exists(filename)
    p = Parser(filename)
