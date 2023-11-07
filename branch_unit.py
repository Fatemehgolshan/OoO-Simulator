from btb import *

class BranchUnit:
    def __init__(self, num_entries):
        self.num_entries = num_entries
        self.btb = [BtbEntry()] * self.num_entries

    def get_index(self, pc):
        return (pc >> 4) % self.num_entries
        
    def is_in_btb(self, pc):
        idx = self.get_index(pc)
        assert idx >= 0 and idx < self.num_entries
        return self.btb[idx].valid and self.btb[idx].pc == pc

    def is_taken(self, pc):
        if not self.is_in_btb(pc): return False
        idx = self.get_index(pc)
        assert idx >= 0 and idx < self.num_entries
        assert self.btb[idx].valid and self.btb[idx].pc == pc
        assert self.btb[idx].cnt >= 0 and self.btb[idx].cnt <= 3
        return self.btb[idx].cnt >= 2

    def get_target(self, pc):
        assert self.is_taken(pc)
        idx = self.get_index(pc)
        assert idx >= 0 and idx < self.num_entries
        assert self.btb[idx].valid and self.btb[idx].pc == pc and self.btb[idx].cnt >= 2
        return self.btb[idx].get_target(pc)

    def update_btb(self, pc, target, is_taken):
        if self.is_in_btb(pc):
            idx = self.get_index(pc)
            assert idx >= 0 and idx < self.num_entries
            assert self.btb[idx].valid and self.btb[idx].pc == pc
            if is_taken:
                self.btb[idx].target = target
                self.btb[idx].increment_cnt()
            else:
                self.btb[idx].decrement_cnt()

        else:
            idx = self.get_index(pc)
            assert idx >= 0 and idx < self.num_entries
            assert (not self.btb[idx].valid) or (self.btb[idx].pc != pc)
            self.btb[idx] = BtbEntry()
            self.btb[idx].set_entry(pc, target, cnt=2)

    def __repr__(self):
        for e in self.btb:
            print(e)
