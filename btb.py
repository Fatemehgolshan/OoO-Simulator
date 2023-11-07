class BtbEntry:
    def __init__(self):
        self.valid = False
        self.pc = 0
        self.target = 0
        self.cnt = 2

    def set_entry(self, pc, target, cnt):
        assert not self.valid
        self.valid = True
        self.pc = pc
        self.target = target
        self.cnt = cnt

    def increment_cnt(self):
        self.cnt = min(self.cnt + 1, 3)

    def decrement_cnt(self):
        self.cnt = max(self.cnt - 1, 0)

    def update_target(self, pc, target):
        assert self.pc == pc
        self.target = target

    def update_cnt(self, pc, is_taken):
        assert self.pc == pc
        if is_taken:
            self.increment_cnt()
        else:
            self.decrement_cnt()

    def get_target(self, pc):
        assert self.pc == pc
        return self.target

    def __repr__(self):
        return f'valid={self.valid}, pc={self.pc}, target={self.target}, cnt={self.cnt}'
