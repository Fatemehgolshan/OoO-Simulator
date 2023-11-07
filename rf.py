'''
Register file
'''


class RegisterFile:
    def __init__(self):
        self.rf = {}


    def read(self, reg):
        if reg not in self.rf.keys():
            self.rf[reg] = 0
        return self.rf[reg]


    def write(self, reg, val):
        self.rf[reg] = val


    def __repr__(self):
        return f'{self.rf}'
