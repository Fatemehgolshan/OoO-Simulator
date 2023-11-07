'''
The processor & memory
'''

import json
import os, sys
from parser import *
from instruction import *
from rf import *
from pipelined_component import *
from scoreboard import *
from branch_unit import *


class Processor:
    def __init__(self, cfg_file, input_file):
        self.parser = Parser(input_file)
        self.mem = {}
        self.regfile = {}
        self.initialize_memory(self.parser.get_mem_initialization())
        self.rf = RegisterFile()
        self.initialize_components(cfg_file)
        self.branch_record = []
        self.scoreboard = Scoreboard()
        self.simulate_func(verbose=True)
        self.simulate_timing(verbose=True)


    def initialize_memory(self, mem_code):
        for k, v in mem_code:
            self.mem[int(k)] = float(v)


    def initialize_components(self, cfg_file):
        with open(cfg_file) as f: cfg = json.load(f)
        self.NF = cfg['NF']
        self.NI = cfg['NI']
        self.NW = cfg['NW']
        self.NR = cfg['NR']
        self.NB = cfg['NB']
        self.decoder = PComponent('Decoder', 1, self.NI)
        self.ex_INT = PComponent('INT', cfg['INT_latency'], cfg['INT_RS'])
        self.ex_LD = PComponent('LD', cfg['LD_latency'], cfg['LD_RS'])
        self.ex_ST = PComponent('ST', cfg['ST_latency'], cfg['ST_RS'])
        self.ex_FPadd = PComponent('FPadd', cfg['FPadd_latency'], cfg['FPadd_RS'])
        self.ex_FPmult = PComponent('FPmult', cfg['FPmult_latency'], cfg['FPmult_RS'])
        self.ex_FPdiv = PComponent('FPdiv', cfg['FPdiv_latency'], cfg['FPdiv_RS'])
        self.ex_BU = PComponent('BU', cfg['BU_latency'], cfg['BU_RS'])
        self.rob = PComponent('ROB', cfg['ROB_latency'], cfg['ROB_RS'])
        self.cache_latency = cfg['cache_latency']
        self.reg_rename = PComponent('RegRename', 0, cfg['num_physical_regs'])
        self.branch_unit = BranchUnit(cfg['btb_entries'])


    def simulate_timing(self, verbose):
        code = self.parser.get_instructions()
        num_code_lines = len(code)

        bottleneck_width = min(self.NF, self.NI, self.NW, self.NR, self.NB)

        def fetch_instructions(pc, num):
            l_begin = pc // 4
            l_end = min(l_begin + num, num_code_lines)
            return code[l_begin:l_end]

        pc = 0
        curr_cycle = 0
        total_exec_cycles = 0
        self.branch_idx = 0
        while True:
            curr_cycle += self.cache_latency    # instruction cache
            fetched_instrs_str = fetch_instructions(pc, min(self.NF, bottleneck_width))

            if len(fetched_instrs_str) == 0:
                if verbose: print(f'execution done. total_exec_cycles={total_exec_cycles}')
                break

            next_pc = pc + 4 * len(fetched_instrs_str)
            for i, instr_str in enumerate(fetched_instrs_str):
                npc, instr, branch_mispred_stall = self.run_instruction(instr_str, pc + 4*i, curr_cycle, verbose)
                total_exec_cycles = max(total_exec_cycles, instr.get_retire_cycle())

                if npc != pc + 4*i + 4:
                    if verbose: print(f'Branch detected: pc:{pc}, npc:{npc}')
                    next_pc = npc

            pc = next_pc
            curr_cycle += branch_mispred_stall


    def run_instruction(self, instr_str, pc, fetch_cycle, verbose):
        '''
        This function runs the entire pipeline from fetch to retire. It returns
        an Instruction instance whose `curr_cycle` is the cycle at which the
        instruction retires.

        `fetch_cycle` is the cycle at which the instruction is already fetched
        into the CPU pipeline; i.e., the L1i latency is passed
        '''
        instr = Instruction(pc, instr_str)
        instr.set_fetch_cycle(fetch_cycle)

        if verbose: print(instr)

        # Decode
        ccycle = fetch_cycle

        wait_time = 0   # reg rename
        for i in range(len(instr.get_src_regs()) + len(instr.get_dest_regs())):
            wait_time += self.reg_rename.get_wait_cycles(ccycle)
        ccycle += wait_time

        wait_time = 0   # dependancy
        for reg in instr.get_src_regs():
            wait_time = max(wait_time, self.scoreboard.get_wait_cycles(reg, ccycle))
        ccycle += wait_time

        decode_cycle = self.decoder.allocate(ccycle)
        instr.set_decode_cycle(decode_cycle)

        branch_mispred_stall = 0

        # Execute & Mem
        operator = instr.get_operator()
        exec_cycle = None
        next_pc = pc + 4
        if operator in ['add', 'addi', 'slt']:
            exec_cycle = self.ex_INT.allocate(decode_cycle)

        elif operator == 'fld':
            exec_cycle = self.ex_LD.allocate(decode_cycle) + self.cache_latency

        elif operator == 'fsd':
            exec_cycle = self.ex_ST.allocate(decode_cycle) + self.cache_latency

        elif operator in ['fadd', 'fsub']:
            exec_cycle = self.ex_FPadd.allocate(decode_cycle)

        elif operator == 'fmul':
            exec_cycle = self.ex_FPmult.allocate(decode_cycle)

        elif operator == 'fdiv':
            exec_cycle = self.ex_FPdiv.allocate(decode_cycle)

        elif operator == 'bne':
            exec_cycle = self.ex_BU.allocate(decode_cycle)
            assert self.branch_idx < len(self.branch_record)
            taken = self.branch_record[self.branch_idx]
            self.branch_idx += 1
            if taken: next_pc = int(instr.get_operands()[-1])

            # predict the branch
            predicted_taken = self.branch_unit.is_taken(pc)

            mispredict = predicted_taken ^ taken
            if taken and predicted_taken:
                if self.branch_unit.get_target(pc) != next_pc:
                    mispredict = True

            if mispredict:
                branch_mispred_stall = self.decoder.get_latency() + self.ex_BU.get_latency()

            # train the branch unit
            self.branch_unit.update_btb(pc, next_pc, taken)

        else:
            assert False, f'Unrecognized operator:{operator}'

        assert exec_cycle != None
        assert exec_cycle > decode_cycle

        for reg in instr.get_dest_regs():
            self.scoreboard.push(reg, exec_cycle)

        # allocate reg rename units retrospectively
        for i in range(len(instr.get_src_regs()) + len(instr.get_dest_regs())):
            self.reg_rename.allocate_timed(decode_cycle, exec_cycle - decode_cycle)

        instr.set_execute_cycle(exec_cycle)

        retire_cycle = self.rob.allocate(exec_cycle)
        instr.set_retire_cycle(retire_cycle)

        return next_pc, instr, branch_mispred_stall



    def simulate_func(self, verbose):
        code = self.parser.get_instructions()
        pc = 0
        while pc / 4 < len(code):
            if verbose: print(self)
            if verbose: print('-'*10)

            line_num = pc // 4
            instr_str = code[line_num]

            instr = Instruction(pc, instr_str)
            operator = instr.get_operator()
            operands = instr.get_operands()
            operand_types = instr.get_operand_types()

            if verbose: print(instr_str)
            if verbose: print('-'*10)
            pc += 4

            if operator == 'fld':
                assert len(operands) == 2
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Memory]
                m = re.search(r'(\d+)\((.*)\)', operands[1])
                assert m
                addr = int(m.group(1)) + self.rf.read(m.group(2))
                val = 0
                if addr in self.mem.keys():
                    val = self.mem[addr]
                else:
                    if verbose: print(f'[Warn] addr:{addr} is not in memory... using 0 as the value')
                self.rf.write(operands[0], val)

            elif operator == 'fsd':
                assert len(operands) == 2
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Memory]
                m = re.search(r'(\d+)\((.*)\)', operands[1])
                assert m
                addr = int(m.group(1)) + self.rf.read(m.group(2))
                self.mem[addr] = self.rf.read(operands[0])

            elif operator == 'add':
                assert len(operands) == 3
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
                self.rf.write(operands[0], self.rf.read(operands[1]) + self.rf.read(operands[2]))

            elif operator == 'addi':
                assert len(operands) == 3
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Immediate]
                self.rf.write(operands[0], self.rf.read(operands[1]) + int(operands[2]))

            elif operator == 'slt':
                assert len(operands) == 3
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
                if self.rf.read(operands[1]) < self.rf.read(operands[2]):
                    self.rf.write(operands[0], 1)
                else:
                    self.rf.write(operands[0], 0)

            elif operator == 'fadd':
                assert len(operands) == 3
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
                self.rf.write(operands[0], self.rf.read(operands[1]) + self.rf.read(operands[2]))

            elif operator == 'fsub':
                assert len(operands) == 3
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
                self.rf.write(operands[0], self.rf.read(operands[1]) - self.rf.read(operands[2]))

            elif operator == 'fmul':
                assert len(operands) == 3
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
                self.rf.write(operands[0], self.rf.read(operands[1]) * self.rf.read(operands[2]))

            elif operator == 'fdiv':
                assert len(operands) == 3
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Register]
                self.rf.write(operands[0], self.rf.read(operands[1]) / self.rf.read(operands[2]))

            elif operator == 'bne':
                assert len(operands) == 3
                assert operand_types == [Instruction.OperandType.Register, Instruction.OperandType.Register, Instruction.OperandType.Immediate]
                taken = False
                if self.rf.read(operands[0]) != self.rf.read(operands[1]):
                    taken = True
                    pc = int(operands[2])

                self.branch_record.append(taken)

            else:
                assert False, f'Unknown operator: {operator}'

        if verbose: print(self)
        if verbose: print('-'*10)


    def __repr__(self):
        return f'memory:\n{self.mem}\nrf:\n{self.rf}\nNF:{self.NF}, NI:{self.NI}, NW:{self.NW}, NR:{self.NR}, NB:{self.NB}\nDecoder:{self.decoder}\nexi_INT:{self.ex_INT}\nex_LD:{self.ex_LD}\nex_ST:{self.ex_ST}\nex_FPadd:{self.ex_FPadd}\nex_FPmult:{self.ex_FPmult}\nex_FPdiv:{self.ex_FPdiv}\nex_BU:{self.ex_BU}'


if __name__ == '__main__':
    if len(sys.argv[1:]) != 2:
        print(f'Usage: {argv[0]} path/to/config/file path/to/input/code')
        exit(1)

    cfg_file = sys.argv[1]
    input_code_file = sys.argv[2]
    assert os.path.exists(cfg_file)
    assert os.path.exists(input_code_file)
    proc = Processor(cfg_file, input_code_file)
    print(proc)
