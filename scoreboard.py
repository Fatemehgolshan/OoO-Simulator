'''
Scoreboard for handling dependancies among instructions
'''

class Scoreboard:
    def __init__(self):
        self.sb = {}


    def push(self, reg, cycle):
        if reg not in self.sb.keys():
            self.sb[reg] = cycle
        self.sb[reg] = max(cycle, self.sb[reg])


    def get_wait_cycles(self, reg, curr_cycle):
        if reg not in self.sb.keys(): return 0
        ready_cycle = self.sb[reg]
        return max(0, ready_cycle - curr_cycle)
