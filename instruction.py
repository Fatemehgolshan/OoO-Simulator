'''
An individual instruction along with its status in the processor pipeline
'''

import re
from enum import Enum


class Instruction:
    class OperandType(Enum):
        Register = 0
        Memory = 1
        Immediate = 2


    class OperandFlow(Enum):
        Src = 0
        Dest = 1
        Immediate = 2


    def __init__(self, pc, instr):
        assert type(pc) == int
        assert type(instr) == str
        self.pc = pc
        self.instr = instr
        self.operator = self.get_operator()
        self.operands = self.get_operands()
        self.operand_types = self.get_operand_types()
        self.operand_flows = self.set_operand_flows()
        self.src_regs = self.get_src_regs()
        self.dest_regs = self.get_dest_regs()
        self.curr_cycle = -1
        self.fetch_cycle = -1
        self.decode_cycle = -1
        self.execute_cycle = -1
        self.retire_cycle = -1


    def set_fetch_cycle(self, cycle):
        self.fetch_cycle = cycle
        self.curr_cycle = cycle


    def get_fetch_cycle(self):
        return self.fetch_cycle


    def set_decode_cycle(self, cycle):
        assert cycle > self.curr_cycle
        self.decode_cycle = cycle
        self.curr_cycle = cycle


    def get_decode_cycle(self):
        return self.decode_cycle


    def set_execute_cycle(self, cycle):
        assert cycle > self.curr_cycle
        self.execute_cycle = cycle
        self.curr_cycle = cycle


    def get_execute_cycle(self):
        return self.execute_cycle


    def set_retire_cycle(self, cycle):
        assert cycle > self.curr_cycle
        self.retire_cycle = cycle
        self.curr_cycle = cycle


    def get_retire_cycle(self):
        return self.retire_cycle


    def get_curr_cycle(self):
        return self.curr_cycle


    def get_operator(self):
        operator = self.instr.split()[0]
        assert operator in ['fld', 'fsd', 'add', 'addi', 'slt', 'fadd', 'fsub', 'fmul', 'fdiv', 'bne']
        return operator


    def get_operands(self):
        operands = ' '.join(self.instr.split()[1:])
        return [x.strip() for x in operands.split(',')]


    def get_operand_types(self):
        return [self.deduct_operand_type(o) for o in self.operands]


    def set_operand_flows(self):
        if self.operator == 'fld':
            assert len(self.operands) == 2
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Memory]
            return [Instruction.OperandFlow.Dest, Instruction.OperandFlow.Src]

        elif self.operator == 'fsd':
            assert len(self.operands) == 2
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Memory]
            return [Instruction.OperandFlow.Src, Instruction.OperandFlow.Dest]

        elif self.operator == 'add':
            assert len(self.operands) == 3
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
            return [Instruction.OperandFlow.Dest, Instruction.OperandFlow.Src, Instruction.OperandFlow.Src]

        elif self.operator == 'addi':
            assert len(self.operands) == 3
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Immediate]
            return [Instruction.OperandFlow.Dest, Instruction.OperandFlow.Src, Instruction.OperandFlow.Immediate]

        elif self.operator == 'slt':
            assert len(self.operands) == 3
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
            return [Instruction.OperandFlow.Dest, Instruction.OperandFlow.Src, Instruction.OperandFlow.Src]

        elif self.operator == 'fadd':
            assert len(self.operands) == 3
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
            return [Instruction.OperandFlow.Dest, Instruction.OperandFlow.Src, Instruction.OperandFlow.Src]

        elif self.operator == 'fsub':
            assert len(self.operands) == 3
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
            return [Instruction.OperandFlow.Dest, Instruction.OperandFlow.Src, Instruction.OperandFlow.Src]

        elif self.operator == 'fmul':
            assert len(self.operands) == 3
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
            return [Instruction.OperandFlow.Dest, Instruction.OperandFlow.Src, Instruction.OperandFlow.Src]

        elif self.operator == 'fdiv':
            assert len(self.operands) == 3
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
            return [Instruction.OperandFlow.Dest, Instruction.OperandFlow.Src, Instruction.OperandFlow.Src]

        elif self.operator == 'bne':
            assert len(self.operands) == 3
            assert self.operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Immediate]
            return [Instruction.OperandFlow.Src, Instruction.OperandFlow.Src, Instruction.OperandFlow.Immediate]

        else:
            assert False, f'Unknown operator: {self.operator}'


    def get_src_regs(self):
        assert len(self.operands) == len(self.operand_flows)
        regs = []
        for i, flow in enumerate(self.operand_flows):
            if flow == Instruction.OperandFlow.Src:
                regs.append(self.get_reg_from_operand(self.operands[i]))
            else:
                assert flow in [Instruction.OperandFlow.Dest, Instruction.OperandFlow.Immediate]
        assert len(regs) > 0
        return regs


    def get_dest_regs(self):
        assert len(self.operands) == len(self.operand_flows)
        regs = []
        for i, flow in enumerate(self.operand_flows):
            if flow == Instruction.OperandFlow.Dest:
                if re.search(r'\d+\((.+\d+)\)', self.operands[i]): continue # memory
                regs.append(self.operands[i])
            else:
                assert flow in [Instruction.OperandFlow.Src, Instruction.OperandFlow.Immediate]
        assert len(regs) <= 1
        return regs


    def get_reg_from_operand(self, operand):
        if re.search(r'\d+\((.+\d+)\)', operand): return self.get_reg_from_mem_operand(operand)
        else: return operand


    def get_reg_from_mem_operand(self, operand):
        m = re.search(r'\d+\((.+\d+)\)', operand)
        assert m
        reg = m.group(1)
        if not self.is_reg(reg):
            print(f'[Warn] {reg} in operand={operand} does not appear to be a register')
        return reg


    def is_reg(self, token):
        return re.search(r'(F|R|\$)\d+', token)


    def deduct_operand_type(self, operand):
        try:
            float(operand)
            return Instruction.OperandType.Immediate
        except ValueError:
            pass

        m = re.search(r'\d+\((.+\d+)\)', operand)
        if m:
            if not self.is_reg(m.group(1)):
                print(f'[Warn] {m.group(1)} in operand={operand} does not appear to be a register')
            return Instruction.OperandType.Memory

        if not self.is_reg(operand):
            print(f'[Warn] {operand} does not appear to be a register')
        return Instruction.OperandType.Register


    def __repr__(self):
        return f'pc={self.pc}, operator={self.operator}, operands={self.operands}, operand_types={self.operand_types}, operand_flows={self.operand_flows}, src_regs={self.src_regs}, dest_regs={self.dest_regs}'


if __name__ == '__main__':
    code = '''\
addi R1, R0, 24
addi R2, R0, 124
fld F2, 200(R0)
fld F0, 0(R1)
fmul F0, F0, F2
fld F4, 0(R2)
fadd F0, F0, F4
fsd F0, 0(R2)
addi R1, R1, -8
addi R2, R2, -8
bne R1,$0, 1000
'''
    for line_num, instr_str in enumerate(code.splitlines()):
        instr = Instruction(line_num * 4, instr_str)
        print(f'instr_str:{instr_str}, instr:{instr}')
        print('-' * 20)
